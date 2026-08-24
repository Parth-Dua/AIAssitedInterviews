import { Task, TaskCreateInput, TaskStatus, TaskUpdateInput } from '../types';
import { TaskRepository } from '../repositories/taskRepository';

export class TaskNotFoundError extends Error {
  constructor(taskId: string) {
    super(`Task not found: ${taskId}`);
    this.name = 'TaskNotFoundError';
  }
}

export class InvalidTaskUpdateError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidTaskUpdateError';
  }
}

const VALID_STATUSES: TaskStatus[] = ['todo', 'in_progress', 'done'];

let nextGeneratedId = 1000;
function generateTaskId(): string {
  return `task-${nextGeneratedId++}`;
}

/**
 * Business logic for reading and mutating tasks. Sits between the
 * controllers (HTTP concerns) and the repository (storage concerns).
 */
export class TaskService {
  constructor(private readonly repository: TaskRepository) {}

  listTasksForBoard(boardId: string): Task[] {
    return this.repository.listByBoard(boardId);
  }

  createTask(boardId: string, input: TaskCreateInput): Task {
    const task: Task = {
      id: generateTaskId(),
      boardId,
      title: input.title,
      status: 'todo',
      priority: input.priority ?? 'medium',
      assigneeId: input.assigneeId ?? null,
    };
    return this.repository.save(task);
  }

  /**
   * Applies a partial update to an existing task. Only fields present in
   * `updates` should change; everything else stays as it was.
   */
  updateTask(taskId: string, updates: TaskUpdateInput): Task {
    const existing = this.repository.getById(taskId);
    if (!existing) {
      throw new TaskNotFoundError(taskId);
    }

    if (updates.status !== undefined && !VALID_STATUSES.includes(updates.status)) {
      throw new InvalidTaskUpdateError(
        `Invalid status: ${updates.status}. Must be one of ${VALID_STATUSES.join(', ')}.`
      );
    }

    const merged: Task = {
      ...existing,
      title: updates.title ?? existing.title,
      priority: updates.priority ?? existing.priority,
      assigneeId:
        updates.assigneeId !== undefined ? updates.assigneeId : existing.assigneeId,
      status: updates.status ?? existing.status,
    };

    return this.repository.save(merged);
  }
}
