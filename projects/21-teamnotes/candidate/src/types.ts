export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  version: number;
}

/** Shape accepted by POST /notes. */
export interface NoteCreateInput {
  title: string;
  content?: string;
  tags?: string[];
}

/** Shape accepted by PUT /notes/:id — the full note as the client's edit
 * form last loaded it, including whatever `version` it was loaded with. */
export interface NoteUpdatePayload {
  title: string;
  content: string;
  tags: string[];
  version: number;
}

/** Summary shape returned by GET /notes (list view). */
export interface NoteSummary {
  id: string;
  title: string;
  tags: string[];
  version: number;
}
