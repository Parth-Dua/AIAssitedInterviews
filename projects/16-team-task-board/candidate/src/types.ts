export type TaskStatus = 'todo' | 'in_progress' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: string;
  boardId: string;
  title: string;
  status: TaskStatus;
  priority: TaskPriority;
  assigneeId: string | null;
}

/** Shape accepted by POST /boards/:boardId/tasks. */
export interface TaskCreateInput {
  title: string;
  priority?: TaskPriority;
  assigneeId?: string | null;
}

/** Shape accepted by PATCH /tasks/:id. Every field is optional — only the
 * fields present in the request body should be changed. */
export interface TaskUpdateInput {
  title?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigneeId?: string | null;
}
