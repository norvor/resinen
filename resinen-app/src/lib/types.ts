export type Sentiment = 'uplifting' | 'neutral' | 'distressing';

export interface Story {
	id: string;
	headline: string;
	summary: string;
	source: string;
	url: string;
	sentiment: Sentiment;
	spectrum: { perspective: string; summary: string; bias: string }[];
	timestamp: string;
}

export interface Quote {
	text: string;
	author: string;
}

export interface CooluteImage {
	url: string;
	caption: string;
}