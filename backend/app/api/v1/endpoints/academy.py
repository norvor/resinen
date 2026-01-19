from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.api import deps # Consistent dependency injection
from app.models.user import User
from app.models.academy import Module, Lesson, LessonCompletion
from app.schemas.academy import ModuleRead, ModuleCreate, LessonCreate

router = APIRouter()

# --- 1. GET CURRICULUM (With User Progress) ---
@router.get("/", response_model=List[ModuleRead])
async def get_curriculum(
    community_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    # A. Fetch Modules & Lessons (Sorted)
    # Added selectinload to ensure lessons are loaded asynchronously before the loop
    stmt = (
        select(Module)
        .where(Module.community_id == community_id)
        .order_by(Module.order_index)
        .options(selectinload(Module.lessons))
    )
    
    # ✅ FIX: Use db.execute() for AsyncSession
    result = await db.execute(stmt)
    modules = result.scalars().all()
    
    # B. Fetch User's Completed IDs
    comp_stmt = select(LessonCompletion.lesson_id).where(LessonCompletion.user_id == current_user.id)
    
    # ✅ FIX: Use db.execute() for AsyncSession
    comp_result = await db.execute(comp_stmt)
    completed_ids = comp_result.scalars().all()
    completed_set = set(completed_ids)

    # C. Assemble & Mark Completed
    final_result = []
    for mod in modules:
        # Manually sort lessons inside the module (Python side)
        sorted_lessons = sorted(mod.lessons, key=lambda l: l.order_index)
        
        lesson_reads = []
        for l in sorted_lessons:
            # model_dump() is the SQLModel/Pydantic v2 way, dict() for v1
            l_dict = l.model_dump() if hasattr(l, 'model_dump') else l.dict()
            l_dict['is_completed'] = (l.id in completed_set)
            lesson_reads.append(l_dict)
            
        mod_read = ModuleRead(
            id=mod.id,
            title=mod.title,
            description=mod.description,
            order_index=mod.order_index,
            lessons=lesson_reads
        )
        final_result.append(mod_read)
        
    return final_result

# --- 2. MARK LESSON COMPLETE ---
@router.post("/lessons/{lesson_id}/complete", response_model=Any)
async def complete_lesson(
    lesson_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    # Idempotent check
    # ✅ FIX: db.get() is fine in AsyncSession, but we use a select for multi-pk if needed
    stmt = select(LessonCompletion).where(
        LessonCompletion.user_id == current_user.id,
        LessonCompletion.lesson_id == lesson_id
    )
    result = await db.execute(stmt)
    existing = result.scalars().first()

    if not existing:
        completion = LessonCompletion(user_id=current_user.id, lesson_id=lesson_id)
        db.add(completion)
        
        # Add XP (Gamification hook)
        current_user.xp += 50
        db.add(current_user)
        
        await db.commit()
        
    return {"status": "success"}

# --- 3. ADMIN: CREATE CONTENT ---
@router.post("/modules", response_model=ModuleRead)
async def create_module(
    mod: ModuleCreate, 
    db: AsyncSession = Depends(deps.get_db)
):
    # ✅ FIX: Use model_validate for SQLModel/Pydantic v2 or from_orm for v1
    new_mod = Module.model_validate(mod) if hasattr(Module, "model_validate") else Module.from_orm(mod)
    db.add(new_mod)
    await db.commit()
    await db.refresh(new_mod)
    return new_mod

@router.post("/modules/{module_id}/lessons", response_model=Any)
async def create_lesson(
    module_id: str, 
    lesson: LessonCreate, 
    db: AsyncSession = Depends(deps.get_db)
):
    lesson_data = lesson.model_dump() if hasattr(lesson, 'model_dump') else lesson.dict()
    new_lesson = Lesson(**lesson_data, module_id=module_id)
    db.add(new_lesson)
    await db.commit()
    await db.refresh(new_lesson)
    return new_lesson