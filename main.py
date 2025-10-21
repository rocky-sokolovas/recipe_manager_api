from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from db_manager import DbManager,NotFoundError,OtherError
from pydantic import BaseModel

engine = "postgresql+psycopg2://postgres:***********/recipe_app"
db=DbManager(engine)


class Ingredient(BaseModel):
    name: str
    description: str
    unit: str
    calories: float
    protein: float
    fat: float
    carbs: float

class UpdateIngredient(BaseModel):
    name: str| None = None
    description: str| None = None
    unit: str| None = None
    calories: float| None = None
    protein: float| None = None
    fat: float| None = None
    carbs: float| None = None


class Recipe(BaseModel):
    name: str
    description: str
    instructions: str
    servings: int
    cooking_time: int
    prep_time: int

class UpdateRecipe(BaseModel):
    name: str| None = None
    description: str| None = None
    instructions: str| None = None
    servings: int| None = None
    cooking_time: int| None = None
    prep_time: int| None = None

class RecipeIngredient(BaseModel):
    ingredient_id: int
    quantity: float

class QuantityUpdate(BaseModel):
    quantity: float

app= FastAPI()

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.args[0]}, # exc.detail contains the message from the exception
    )
@app.exception_handler(IntegrityError)
async def integrity__exception_handler(exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.args[0]}, # exc.detail contains the message from the exception
    )

@app.exception_handler(OtherError)
async def other_exception_handler(exc: OtherError):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.args[0]}, # exc.detail contains the message from the exception
    )

@app.get("/")
async def root():
    return {"message": "This is my Recipe API"}

@app.get("/ingredients")
async def all_ingredients():
    with db.get_session() as session:
        return db.get_all_ingredients(session)

@app.get("/ingredients/{ingredient_id}")
async def get_ingredient(ingredient_id:int):
    with db.get_session() as session:
        return db.get_ingredient_by_id(session,ingredient_id)

@app.post("/ingredients")
async def add_ingredient(ingredient: Ingredient):
    with db.get_session() as session:
        return db.add_ingredient(session,ingredient.name,ingredient.description,ingredient.unit,ingredient.calories,ingredient.protein,ingredient.fat,ingredient.carbs)

@app.delete("/ingredients/{ingredient_id}")
async def delete_ingredient(ingredient_id:int):
    with db.get_session() as session:
        return db.delete_ingredient_by_id(session,ingredient_id)

@app.patch("/ingredients/{ingredient_id}")
async def update_ingredient(ingredient_id:int, ingredient:UpdateIngredient):
    update_data = ingredient.model_dump(exclude_unset=True)
    with db.get_session() as session:
        return db.update_ingredient_by_id(session,ingredient_id,**update_data)

@app.get("/recipes")
async def all_recipes():
    with db.get_session() as session:
            return db.get_all_recipes(session)


@app.post("/recipes")
async def create_recipe(recipe: Recipe):
    with db.get_session() as session:
        return db.add_recipe(session,recipe.name,recipe.description, recipe.instructions,recipe.servings, recipe.cooking_time, recipe.prep_time)

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id:int):
    with db.get_session() as session:
        return db.get_recipe_by_id(session,recipe_id)

@app.patch("/recipes/{recipe_id}")
async def update_recipe(recipe_id:int, recipe:UpdateRecipe):
    update_data = recipe.model_dump(exclude_unset=True)
    with db.get_session() as session:
        return db.update_recipe_by_id(session,recipe_id,**update_data)

@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id:int):
    with db.get_session() as session:
        return db.delete_recipe_by_id(session,recipe_id)

@app.get("/recipes/{recipe_id}/ingredients")
async def all_recipe_ingredients(recipe_id:int):
    with db.get_session() as session:
        return db.get_all_recipe_ingredients(session,recipe_id)

@app.post("/recipes/{recipe_id}/ingredients")
async def create_recipe_ingredient(recipe_id:int,recipe_ing: RecipeIngredient):
    with db.get_session() as session:
        return db.add_recipe_ingredients(session,recipe_id, recipe_ing.ingredient_id, recipe_ing.quantity)

@app.get("/recipes/{recipe_id}/ingredients/{ingredient_id}")
async def get_recipe_ingredient(recipe_id:int,ingredient_id:int):
    with db.get_session() as session:
        return db.get_recipe_ingredient(session,recipe_id,ingredient_id)

@app.patch("/recipes/{recipe_id}/ingredients/{ingredient_id}")
async def update_recipe_ingredient(recipe_id:int,ingredient_id:int,quantity:QuantityUpdate):
    with db.get_session() as session:
        return db.update_recipe_qty(session,recipe_id,ingredient_id,quantity.quantity)

@app.delete("/recipes/{recipe_id}/ingredients")
async def delete_recipe_ingredients(recipe_id:int):
    with db.get_session() as session:
        return db.delete_all_recipe_ingredients(session,recipe_id)

@app.delete("/recipes/{recipe_id}/ingredients/{ingredient_id}")
async def delete_recipe_ingredient(recipe_id:int,ingredient_id:int):
    with db.get_session() as session:
        return db.delete_recipe_ingredient(session,recipe_id,ingredient_id)

@app.get("/mealplan/randomrecipe")
async def get_random_recipe():
    with db.get_session()as session:
        return db.get_random_recipe(session)

@app.get("/mealplan/recipes/")
async def get_recipes_from_ingredient(ingredients:set):
    with db.get_session()as session:
        return db.get_common_recipes(session,ingredients)
#Update to request the information as a parameter
@app.get("/mealplan/plan")
async def get_meal_plan(recipe_nr:int):
    with db.get_session() as session:
        return db.generate_meal_plan(session,recipe_nr)

@app.post("/mealplan/shopping")
async def generate_shopping_list(servings:int,recipes:set):
    with db.get_session() as session:
        return db.get_shopping_list(session,servings,recipes)

