import { Router } from 'express';
import { listTasks, createTask, updateTask } from '../controllers/taskController';
import { validateTaskCreate } from '../middleware/validateTaskCreate';

const router = Router();

router.get('/boards/:boardId/tasks', listTasks);
router.post('/boards/:boardId/tasks', validateTaskCreate, createTask);
router.patch('/tasks/:id', updateTask);

export default router;
