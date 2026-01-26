export interface SpectrumPerspective {
    perspective: string; // e.g. "Claude (Safety)"
    summary: string;
    bias?: string; // e.g. "Pro-Reg"
}

export interface Story {
    id: string;
    headline: string;
    source: string;
    sentiment: 'neutral' | 'uplifting' | 'distressing';
    url: string;
    summary: string;
    timestamp: string;
    category?: string;
    spectrum: SpectrumPerspective[]; // Array of viewpoints
}

export interface Quote {
    text: string;
    author: string;
}

export interface CooluteImage {
    url: string;
    caption: string;
}