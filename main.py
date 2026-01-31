from fastapi import FastAPI 
from fastapi.responses import JSONResponse 
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from db_manager import DbManager,NotFoundError,OtherError
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
engine = os.getenv("ENGINE")
db=DbManager(engine)


class Ingredient(BaseModel):
    ingredient_name: str
    ingredient_description: str
    ingredient_unit: str

class UpdateIngredient(BaseModel):
    ingredient_name: str| None = None
    ingredient_description: str| None = None
    ingredient_unit: str| None = None


class Recipe(BaseModel):
    recipe_name: str
    recipe_description: str
    recipe_instructions: str
    recipe_servings: int
    recipe_cooking_time: int
    recipe_prep_time: int
    recipe_calories: float
    recipe_protein: float
    recipe_fat: float
    recipe_carbs: float

class UpdateRecipe(BaseModel):
    recipe_name: str| None = None
    recipe_description: str| None = None
    recipe_instructions: str| None = None
    recipe_servings: int| None = None
    recipe_cooking_time: int| None = None
    recipe_prep_time: int| None = None
    recipe_calories: float| None = None
    recipe_protein: float| None = None
    recipe_fat: float| None = None
    recipe_carbs: float| None = None

class RecipeIngredient(BaseModel):
    """Pydantic model for adding an ingredient to a recipe."""
    ingredient_id: int
    quantity: float

class QuantityUpdate(BaseModel):
    """Pydantic model for updating the quantity of an existing recipe ingredient association."""
    quantity: float

app= FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(exc: NotFoundError):
    """Handles custom NotFoundError and returns a 404 response."""
    return JSONResponse(
        status_code=404,
        content={"detail": exc.args[0]}, # exc.detail contains the message from the exception
    )
@app.exception_handler(IntegrityError)
async def integrity__exception_handler(exc: IntegrityError):
    """Handles SQLAlchemy IntegrityError (e.g., unique constraint violation) and returns a 409 response."""
    return JSONResponse(
        status_code=409,
        content={"detail": exc.args[0]}, # exc.detail contains the message from the exception
    )

@app.exception_handler(OtherError)
async def other_exception_handler(exc: OtherError):
    """Handles custom OtherError (for general database errors) and returns a 500 response."""
    return JSONResponse(
        status_code=500,
        content={"detail": exc.args[0]}, # exc.detail contains the message from the exception
    )

# --- General Endpoint ---

@app.get("/")
async def root():
    """Returns a simple greeting message for the root path."""
    return {"message": "This is my Recipe API"}

# --- Ingredient Endpoints ---

@app.get("/ingredients")
async def all_ingredients():
    """
    Retrieves a list of all ingredients in the database.
    """
    with db.get_session() as session:
        return db.get_all_ingredients(session)

@app.get("/ingredients/{ingredient_id}")
async def get_ingredient(ingredient_id:int):
    """
    Retrieves a single ingredient by its ID.
    Raises 404 if the ingredient is not found.
    """
    with db.get_session() as session:
        return db.get_ingredient_by_id(session,ingredient_id)

@app.post("/ingredients")
async def add_ingredient(ingredient: Ingredient):
    """
    Creates a new ingredient in the database.
    Body: Ingredient (Pydantic model).
    Raises 409 if an ingredient with the same name already exists.
    """
    with db.get_session() as session:
        return db.add_ingredient(session,ingredient.ingredient_name
                                 ,ingredient.ingredient_description
                                 ,ingredient.ingredient_unit
                                 )

@app.delete("/ingredients/{ingredient_id}")
async def delete_ingredient(ingredient_id:int):
    """
    Deletes an ingredient by its ID.
    Raises 404 if the ingredient is not found.
    """
    with db.get_session() as session:
        return db.delete_ingredient_by_id(session,ingredient_id)

@app.patch("/ingredients/{ingredient_id}")
async def update_ingredient(ingredient_id:int, ingredient:UpdateIngredient):
    """
    Updates one or more attributes of an existing ingredient by ID.
    Body: UpdateIngredient (Pydantic model, partial update allowed).
    Raises 404 if the ingredient is not found.
    """
    # Convert Pydantic model to dict, excluding fields that weren't provided (None)
    update_data = ingredient.model_dump(exclude_unset=True)
    with db.get_session() as session:
        return db.update_ingredient_by_id(session,ingredient_id,**update_data)

# --- Recipe Endpoints ---

@app.get("/recipes")
async def all_recipes():
    """
    Retrieves a list of all recipes in the database.
    """
    with db.get_session() as session:
            return db.get_all_recipes(session)


@app.post("/recipes")
async def create_recipe(recipe: Recipe):
    """
    Creates a new recipe in the database.
    Body: Recipe (Pydantic model).
    Raises 409 if a recipe with the same name already exists.
    """
    with db.get_session() as session:
        return db.add_recipe(session,recipe.recipe_name,recipe.recipe_description
                             , recipe.recipe_instructions,recipe.recipe_servings
                             , recipe.recipe_cooking_time, recipe.recipe_prep_time
                             , recipe.recipe_calories, recipe.recipe_protein
                             , recipe.recipe_fat, recipe.recipe_carbs)

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id:int):
    """
    Retrieves a single recipe by its ID.
    Raises 404 if the recipe is not found.
    """
    with db.get_session() as session:
        return db.get_recipe_by_id(session,recipe_id)

@app.patch("/recipes/{recipe_id}")
async def update_recipe(recipe_id:int, recipe:UpdateRecipe):
    """
    Updates one or more attributes of an existing recipe by ID.
    Body: UpdateRecipe (Pydantic model, partial update allowed).
    Raises 404 if the recipe is not found.
    """
    # Convert Pydantic model to dict, excluding fields that weren't provided (None)
    update_data = recipe.model_dump(exclude_unset=True)
    with db.get_session() as session:
        return db.update_recipe_by_id(session,recipe_id,**update_data)

@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id:int):
    """
    Deletes a recipe by its ID. This also deletes all associated recipe-ingredient links.
    Raises 404 if the recipe is not found.
    """
    with db.get_session() as session:
        return db.delete_recipe_by_id(session,recipe_id)

# --- Recipe Ingredient Association Endpoints ---

@app.get("/recipes/{recipe_id}/ingredients")
async def all_recipe_ingredients(recipe_id:int):
    """
    Retrieves all ingredients and their quantities for a specific recipe.
    Raises 404 if the recipe or its ingredients are not found.
    """
    with db.get_session() as session:
        return db.get_all_recipe_ingredients(session,recipe_id)

@app.post("/recipes/{recipe_id}/ingredients")
async def create_recipe_ingredient(recipe_id:int,recipe_ing: RecipeIngredient):
    """
    Adds an ingredient to a recipe with a specified quantity.
    Body: RecipeIngredient (Pydantic model).
    Raises 404 if the recipe/ingredient ID is invalid.
    Raises 409 if the ingredient is already associated with the recipe.
    """
    with db.get_session() as session:
        return db.add_recipe_ingredients(session,recipe_id, recipe_ing.ingredient_id, recipe_ing.quantity)

@app.get("/recipes/{recipe_id}/ingredients/{ingredient_id}")
async def get_recipe_ingredient(recipe_id:int,ingredient_id:int):
    """
    Retrieves the quantity of a specific ingredient within a specific recipe.
    Raises 404 if the recipe or the association is not found.
    """
    with db.get_session() as session:
        return db.get_recipe_ingredient(session,recipe_id,ingredient_id)

@app.patch("/recipes/{recipe_id}/ingredients/{ingredient_id}")
async def update_recipe_ingredient(recipe_id:int,ingredient_id:int,quantity:QuantityUpdate):
    """
    Updates the quantity of a specific ingredient in a specific recipe.
    Body: QuantityUpdate (Pydantic model).
    Raises 404 if the recipe or the association is not found.
    """
    with db.get_session() as session:
        return db.update_recipe_qty(session,recipe_id,ingredient_id,quantity.quantity)

@app.delete("/recipes/{recipe_id}/ingredients")
async def delete_recipe_ingredients(recipe_id:int):
    """
    Deletes ALL ingredient associations for a given recipe.
    Raises 404 if the recipe is not found.
    """
    with db.get_session() as session:
        return db.delete_all_recipe_ingredients(session,recipe_id)

@app.delete("/recipes/{recipe_id}/ingredients/{ingredient_id}")
async def delete_recipe_ingredient(recipe_id:int,ingredient_id:int):
    """
    Deletes a specific ingredient association from a recipe.
    Raises 404 if the recipe or the association is not found.
    """
    with db.get_session() as session:
        return db.delete_recipe_ingredient(session,recipe_id,ingredient_id)

# --- Meal Planning Endpoints ---

@app.get("/mealplan/randomrecipe")
async def get_random_recipe():
    """
    Retrieves a single random recipe.
    """
    with db.get_session()as session:
        return db.get_random_recipe(session)

@app.get("/mealplan/recipes/")
async def get_recipes_from_ingredient(ingredients:set):
    """
    Retrieves recipes that contain ALL ingredients specified in the query parameter set.
    Query Parameter: ingredients (a set of ingredient IDs).
    """
    with db.get_session()as session:
        return db.get_common_recipes(session,ingredients)
#Update to request the information as a parameter
@app.get("/mealplan/plan")
async def get_meal_plan(recipe_nr:int):
    """
    Generates a meal plan (a set of recipes) trying to link them by shared ingredients.
    Query Parameter: recipe_nr (the desired number of recipes).
    """
    with db.get_session() as session:
        return db.generate_meal_plan(session,recipe_nr)

@app.post("/mealplan/shopping")
async def generate_shopping_list(servings:int,recipes:set):
    """
    Generates a consolidated shopping list for a set of recipes, adjusted for a target serving size.
    Query Parameter: servings (the target servings for each recipe).
    Body: recipes (a set of Recipe IDs).
    """
    with db.get_session() as session:
        return db.get_shopping_list(session,servings,recipes)
