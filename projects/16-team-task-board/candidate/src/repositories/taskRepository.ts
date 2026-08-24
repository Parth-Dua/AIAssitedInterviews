import { Task } from '../types';

/**
 * In-memory store of tasks, keyed by task id. In production this would be
 * backed by a real database table; for this exercise a Map is enough.
 */
export class TaskRepository {
  private readonly tasksById: Map<string, Task> = new Map();

  constructor(seed: Task[] = []) {
    for (const task of seed) {
      this.tasksById.set(task.id, task);
    }
  }

  getById(id: string): Task | undefined {
    return this.tasksById.get(id);
  }

  listByBoard(boardId: string): Task[] {
    return Array.from(this.tasksById.values()).filter(
      (task) => task.boardId === boardId
    );
  }

  save(task: Task): Task {
    this.tasksById.set(task.id, task);
    return task;
  }

  /** Test/dev helper: not used by request handlers. */
  clear(): void {
    this.tasksById.clear();
  }

  /** Test/dev helper: replace all stored tasks with the given set. */
  resetWith(tasks: Task[]): void {
    this.clear();
    for (const task of tasks) {
      this.tasksById.set(task.id, task);
    }
  }
}

let nextSeedId = 1;
function seedTask(
  boardId: string,
  title: string,
  status: Task['status'],
  priority: Task['priority'],
  assigneeId: string | null
): Task {
  const id = `task-${nextSeedId++}`;
  return { id, boardId, title, status, priority, assigneeId };
}

export function createSeedTasks(): Task[] {
  nextSeedId = 1;
  return [
    seedTask('board-1', 'Set up CI pipeline', 'done', 'high', 'user-1'),
    seedTask('board-1', 'Write API docs', 'in_progress', 'medium', 'user-2'),
    seedTask('board-1', 'Fix flaky login test', 'todo', 'high', 'user-1'),
    seedTask('board-1', 'Design task board schema', 'todo', 'medium', null),
    seedTask('board-2', 'Plan Q3 roadmap', 'in_progress', 'high', 'user-3'),
    seedTask('board-2', 'Review vendor contracts', 'todo', 'low', 'user-3'),
    seedTask('board-2', 'Onboard new hire', 'done', 'medium', 'user-2'),
  ];
}

/** Default repository instance used by the app, seeded with sample data. */
export const taskRepository = new TaskRepository(createSeedTasks());
