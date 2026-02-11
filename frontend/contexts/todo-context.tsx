'use client';

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { Task, TaskCreate, TaskUpdate } from '../types';
import { todoService } from '../services/todo-service';

interface TodoState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
}

interface TodoAction {
  type: string;
  payload?: any;
}

interface TodoContextType {
  state: TodoState;
  fetchTasks: () => Promise<void>;
  createTask: (taskData: TaskCreate) => Promise<void>;
  updateTask: (id: string, taskData: TaskUpdate) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  toggleTaskCompletion: (id: string) => Promise<void>;
}

const initialState: TodoState = {
  tasks: [],
  loading: false,
  error: null,
};

const TodoContext = createContext<TodoContextType | undefined>(undefined);

// Action types
const FETCH_TASKS_START = 'FETCH_TASKS_START';
const FETCH_TASKS_SUCCESS = 'FETCH_TASKS_SUCCESS';
const FETCH_TASKS_ERROR = 'FETCH_TASKS_ERROR';
const CREATE_TASK_SUCCESS = 'CREATE_TASK_SUCCESS';
const UPDATE_TASK_SUCCESS = 'UPDATE_TASK_SUCCESS';
const DELETE_TASK_SUCCESS = 'DELETE_TASK_SUCCESS';
const TOGGLE_TASK_COMPLETION = 'TOGGLE_TASK_COMPLETION';

const todoReducer = (state: TodoState, action: TodoAction): TodoState => {
  switch (action.type) {
    case FETCH_TASKS_START:
      return {
        ...state,
        loading: true,
        error: null,
      };
    case FETCH_TASKS_SUCCESS:
      return {
        ...state,
        tasks: action.payload,
        loading: false,
        error: null,
      };
    case FETCH_TASKS_ERROR:
      return {
        ...state,
        loading: false,
        error: action.payload,
      };
    case CREATE_TASK_SUCCESS:
      return {
        ...state,
        tasks: [...state.tasks, action.payload],
      };
    case UPDATE_TASK_SUCCESS:
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id ? action.payload : task
        ),
      };
    case DELETE_TASK_SUCCESS:
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload),
      };
    case TOGGLE_TASK_COMPLETION:
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id ? { ...task, completed: action.payload.completed } : task
        ),
      };
    default:
      return state;
  }
};

export const TodoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(todoReducer, initialState);

  const fetchTasks = async () => {
    dispatch({ type: FETCH_TASKS_START });
    try {
      const tasks = await todoService.getTasks();
      dispatch({ type: FETCH_TASKS_SUCCESS, payload: tasks });
    } catch (error: any) {
      dispatch({ type: FETCH_TASKS_ERROR, payload: error.message });
    }
  };

  const createTask = async (taskData: TaskCreate) => {
    try {
      const newTask = await todoService.createTask(taskData);
      dispatch({ type: CREATE_TASK_SUCCESS, payload: newTask });
    } catch (error: any) {
      dispatch({ type: FETCH_TASKS_ERROR, payload: error.message });
    }
  };

  const updateTask = async (id: string, taskData: TaskUpdate) => {
    try {
      const updatedTask = await todoService.updateTask(id, taskData);
      dispatch({ type: UPDATE_TASK_SUCCESS, payload: updatedTask });
    } catch (error: any) {
      dispatch({ type: FETCH_TASKS_ERROR, payload: error.message });
    }
  };

  const deleteTask = async (id: string) => {
    try {
      await todoService.deleteTask(id);
      dispatch({ type: DELETE_TASK_SUCCESS, payload: id });
    } catch (error: any) {
      dispatch({ type: FETCH_TASKS_ERROR, payload: error.message });
    }
  };

  const toggleTaskCompletion = async (id: string) => {
    try {
      const result = await todoService.toggleTaskCompletion(id);
      dispatch({ type: TOGGLE_TASK_COMPLETION, payload: result });
    } catch (error: any) {
      dispatch({ type: FETCH_TASKS_ERROR, payload: error.message });
    }
  };

  // Fetch tasks when the provider mounts
  useEffect(() => {
    fetchTasks();
  }, []);

  const value = {
    state,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
  };

  return <TodoContext.Provider value={value}>{children}</TodoContext.Provider>;
};

export const useTodo = () => {
  const context = useContext(TodoContext);
  if (!context) {
    throw new Error('useTodo must be used within a TodoProvider');
  }
  return context;
};