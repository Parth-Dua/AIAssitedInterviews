import { User } from '../types';

/**
 * In-memory store of users, keyed by user id. In production this would be
 * backed by a real database table; for this exercise a Map is enough.
 */
export class UserRepository {
  private readonly usersById: Map<string, User> = new Map();

  constructor(seed: User[] = []) {
    for (const user of seed) {
      this.usersById.set(user.id, user);
    }
  }

  getById(id: string): User | undefined {
    return this.usersById.get(id);
  }

  list(): User[] {
    return Array.from(this.usersById.values());
  }
}

export function createSeedUsers(): User[] {
  return [
    { id: 'user-1', name: 'Alice Employee', role: 'employee' },
    { id: 'user-2', name: 'Bob Employee', role: 'employee' },
    { id: 'user-3', name: 'Carla Manager', role: 'manager' },
    { id: 'user-4', name: 'Dave Manager', role: 'manager' },
    { id: 'user-5', name: 'Erin Admin', role: 'admin' },
  ];
}

/** Default repository instance used by the app, seeded with sample data. */
export const userRepository = new UserRepository(createSeedUsers());
