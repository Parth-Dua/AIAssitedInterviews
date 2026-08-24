import { TaskRepository, createSeedTasks } from '../src/repositories/taskRepository';
import { TaskService, TaskNotFoundError } from '../src/services/taskService';

function makeService(): TaskService {
  return new TaskService(new TaskRepository(createSeedTasks()));
}

describe('TaskService.createTask', () => {
  it('defaults a new task to status "todo"', () => {
    const service = makeService();
    const task = service.createTask('board-1', { title: 'Write onboarding guide' });

    expect(task.status).toBe('todo');
    expect(task.title).toBe('Write onboarding guide');
    expect(task.boardId).toBe('board-1');
  });
});

describe('TaskService.updateTask', () => {
  it('updates only the title and leaves status/priority/assigneeId untouched', () => {
    const service = makeService();
    const before = service.listTasksForBoard('board-1')[0];

    const updated = service.updateTask(before.id, { title: 'Renamed task' });

    expect(updated.title).toBe('Renamed task');
    expect(updated.status).toBe(before.status);
    expect(updated.priority).toBe(before.priority);
    expect(updated.assigneeId).toBe(before.assigneeId);
  });

  it('updates only the priority and leaves other fields untouched', () => {
    const service = makeService();
    const before = service.listTasksForBoard('board-1')[0];

    const updated = service.updateTask(before.id, { priority: 'high' });

    expect(updated.priority).toBe('high');
    expect(updated.title).toBe(before.title);
    expect(updated.status).toBe(before.status);
    expect(updated.assigneeId).toBe(before.assigneeId);
  });

  it('moves a task from "todo" to "in_progress" when status is updated', () => {
    // Reproduces the support report: moving a task from 'todo' to
    // 'in_progress' via the update endpoint should actually change the
    // stored status.
    const service = makeService();
    const before = service.listTasksForBoard('board-1').find((t) => t.status === 'todo');
    expect(before).toBeDefined();

    const updated = service.updateTask(before!.id, { status: 'in_progress' });

    expect(updated.status).toBe('in_progress');
  });

  it('throws TaskNotFoundError for an unknown task id', () => {
    const service = makeService();

    expect(() => service.updateTask('does-not-exist', { title: 'x' })).toThrow(
      TaskNotFoundError
    );
  });
});
