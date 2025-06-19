from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
import models
from database import get_db
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category_for_user(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new category for the current authenticated user.
    """
    return crud.create_user_category(db=db, category=category, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Category])
def read_user_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve all categories for the current authenticated user.
    """
    categories = crud.get_categories_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=schemas.Category)
def read_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve a specific category by its ID.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db_category.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this category")
    return db_category

@router.put("/{category_id}", response_model=schemas.Category)
def update_user_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a category for the current authenticated user.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db_category.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this category")
    return crud.update_category(db=db, category_id=category_id, category_update=category_update)

@router.delete("/{category_id}", response_model=schemas.Category)
def delete_user_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a category for the current authenticated user.
    """
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if db_category.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this category")
    return crud.delete_category(db=db, category_id=category_id)
