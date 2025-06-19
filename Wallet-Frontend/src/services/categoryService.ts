import api from './api';
import { Category, CategoryType } from '../models/Category';

export interface CategoryCreateRequest {
  name: string;
  type: CategoryType;
}

export interface CategoryUpdateRequest {
  name?: string;
  type?: CategoryType;
}

export const categoryService = {
  async getCategories(): Promise<Category[]> {
    const response = await api.get('/categories');
    return response.data;
  },

  async getCategory(id: number): Promise<Category> {
    const response = await api.get(`/categories/${id}`);
    return response.data;
  },

  async createCategory(category: CategoryCreateRequest): Promise<Category> {
    const response = await api.post('/categories', category);
    return response.data;
  },

  async updateCategory(id: number, category: CategoryUpdateRequest): Promise<Category> {
    const response = await api.put(`/categories/${id}`, category);
    return response.data;
  },

  async deleteCategory(id: number): Promise<Category> {
    const response = await api.delete(`/categories/${id}`);
    return response.data;
  },

  async getCategorySpending(transactions: any[]): Promise<{ name: string; value: number; color: string }[]> {
    const categories = await this.getCategories();
    const categorySpending: { [key: string]: number } = {};
    
    // Calculate spending by category
    transactions
      .filter(t => t.type === 'EXPENSE' && t.category_id)
      .forEach(t => {
        const category = categories.find(c => c.id === t.category_id);
        if (category) {
          categorySpending[category.name] = (categorySpending[category.name] || 0) + Math.abs(t.amount);
        }
      });

    // Convert to chart format with colors
    const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#f97316'];
    
    return Object.entries(categorySpending).map(([name, value], index) => ({
      name,
      value,
      color: colors[index % colors.length],
    }));
  },
}; 