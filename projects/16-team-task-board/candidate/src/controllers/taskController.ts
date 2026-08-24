import { Request, Response } from 'express';
import { TaskService, TaskNotFoundError } from '../services/taskService';
import { taskRepository } from '../repositories/taskRepository';

const taskService = new TaskService(taskRepository);

export function listTasks(req: Request, res: Response): void {
  const { boardId } = req.params;
  const tasks = taskService.listTasksForBoard(boardId);
  res.status(200).json(tasks);
}

export function createTask(req: Request, res: Response): void {
  const { boardId } = req.params;
  const task = taskService.createTask(boardId, req.body ?? {});
  res.status(201).json(task);
}

export function updateTask(req: Request, res: Response): void {
  const { id } = req.params;

  try {
    const task = taskService.updateTask(id, req.body ?? {});
    res.status(200).json(task);
  } catch (err) {
    if (err instanceof TaskNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}
