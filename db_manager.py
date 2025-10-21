from sqlalchemy import create_engine, String,Integer, ForeignKey, select, delete, update,exc,func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session,DeclarativeBase,Mapped,mapped_column,relationship,joinedload
import random

class NotFoundError(Exception):
    pass

class OtherError(Exception):
    pass


class Base(DeclarativeBase):
    pass

class Ingredient(Base):    
    __tablename__ = "ingredients"

    ingredient_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    ingredient_name: Mapped[str] = mapped_column(String(50), unique=True)
    ingredient_description: Mapped[str] = mapped_column(String(200),nullable=True)
    ingredient_unit: Mapped[str] = mapped_column(String(10),nullable=True)
    ingredient_calories: Mapped[float] = mapped_column(nullable=True)
    ingredient_protein: Mapped[float] = mapped_column(nullable=True)
    ingredient_fat: Mapped[float] = mapped_column(nullable=True)
    ingredient_carbs: Mapped[float] = mapped_column(nullable=True)
    recipe_associations: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )
class Recipe(Base):
    __tablename__ = "recipes"

    recipe_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_name: Mapped[str] = mapped_column(String(50), unique=True)
    recipe_description: Mapped[str] = mapped_column(String(200),nullable=True)
    recipe_instructions: Mapped[str] = mapped_column(String(5000))
    recipe_servings: Mapped[int] = mapped_column(Integer())
    recipe_cooking_time: Mapped[int] = mapped_column(nullable=True)
    recipe_prep_time: Mapped[int] = mapped_column(nullable=True)
    ingredient_associations: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_ingredients_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.recipe_id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.ingredient_id"))
    ingredient_quantity: Mapped[float]


    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_associations")
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredient_associations")


class DbManager:
    def __init__(self,engine:str):
        self.engine=create_engine(engine)
        self.create_database()
    
    def create_database(self):
        Base.metadata.create_all(self.engine)
    
    def get_session(self)->Session:
        return Session(self.engine)
    
    def commit_session(self, session:Session):
            try:
                session.commit()
            except exc.IntegrityError as e:
                session.rollback()
                raise IntegrityError(e)
            except Exception as e:
                session.rollback()
                raise OtherError(e)
            else:
                return True

    #   INGREDIENT CRUD #

    def add_ingredient(self,session:Session
                       ,ingredient_name:str,ingredient_description:str,ingredient_unit:str
                       ,ingredient_calories:float,ingredient_protein:float,ingredient_fat:float
                       ,ingredient_carbs:float)->int| None:
        new_ingredient=Ingredient(
                ingredient_name=ingredient_name,
                ingredient_description=ingredient_description,
                ingredient_unit=ingredient_unit,
                ingredient_calories=ingredient_calories,
                ingredient_protein=ingredient_protein,
                ingredient_fat=ingredient_fat,
                ingredient_carbs=ingredient_carbs
            )
        session.add(new_ingredient)
        if self.commit_session(session):
            return new_ingredient.ingredient_id

    def get_all_ingredients(self,session:Session)->list[Ingredient]| None:
        return session.scalars(select(Ingredient).order_by(Ingredient.ingredient_id)).all()

    def get_ingredient_by_id(self,session:Session, id:int)->Ingredient| None:
        ingredient= session.get(Ingredient,id)
        if not ingredient:
            raise NotFoundError("Ingredient Not Found.")
        else:
            return ingredient

    def get_ingredient_id(self,session:Session,key:str,value)->int| None:
        if hasattr(Ingredient,key):
            ingredient=session.scalars(select(Ingredient).where(getattr(Ingredient,key)==value)).first()
            if not ingredient:
                raise NotFoundError("Ingredient Not Found.")
            return ingredient.ingredient_id

    def update_ingredient_by_id(self,session:Session, id:int, **kwargs)->int| None:
        ingredient=session.get(Ingredient,id)
        if not ingredient:
            raise NotFoundError("Ingredient Not Found.")
        for key,value in kwargs.items():
            if hasattr(ingredient, key):
                setattr(ingredient,key,value)
        if self.commit_session(session):
            return ingredient.ingredient_id

    def delete_ingredient_by_id(self,session:Session, id:int)->Ingredient| None:
        ingredient=session.get(Ingredient,id)
        if not ingredient:
            raise NotFoundError("Ingredient Not Found.")
        session.delete(ingredient)
        if self.commit_session(session):
            return ingredient

    #   RECIPE CRUD #

    def add_recipe(self,session:Session,recipe_name:str,recipe_description:str
                   ,recipe_instructions:str,recipe_servings:int,recipe_cooking_time:int
                   ,recipe_prep_time:int)->int| None:
        new_recipe=Recipe(
                recipe_name=recipe_name,
                recipe_description=recipe_description,
                recipe_instructions=recipe_instructions,
                recipe_servings=recipe_servings,
                recipe_cooking_time=recipe_cooking_time,
                recipe_prep_time=recipe_prep_time
            )
        session.add(new_recipe)
        if self.commit_session(session):
            return new_recipe.recipe_id

    def get_all_recipes(self,session:Session)->list[Recipe]| None:
        return session.scalars(select(Recipe).order_by(Recipe.recipe_id)).all()

    def get_recipe_by_id(self,session:Session, id:int)->Recipe| None:
        recipe =  session.get(Recipe,id)
        if not recipe:
            raise NotFoundError("Recipe Not Found.")
        else:
            return recipe

    def update_recipe_by_id(self,session:Session, id:int, **kwargs)->int| None:
        recipe=session.get(Recipe,id)
        if not recipe:
            raise NotFoundError("Recipe Not Found.")
        for key,value in kwargs.items():
            if hasattr(recipe, key):
                setattr(recipe,key,value)
        if self.commit_session(session):
            return recipe.recipe_id

    def delete_recipe_by_id(self,session:Session, id:int)->Recipe| None:
        recipe=session.get(Recipe,id)
        if not recipe:
            raise NotFoundError("Recipe Not Found.")
        session.delete(recipe)
        if self.commit_session(session):
            return recipe
    
    def get_recipe_id(self,session:Session,key:str,value)->int| None:
        if hasattr(Recipe,key):
            recipe=session.scalars(select(Recipe).where(getattr(Recipe,key)==value)).first()
            if not recipe:
                raise NotFoundError("Recipe Not Found.")
            return recipe.recipe_id

    #   RECIPE_INGREDIENT CRUD  #

    def get_recipe_ingredient(self,session:Session,recipe:int,ingredient:int)->dict:
        try:
            self.get_recipe_by_id(session,recipe)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            stmt = (
                select(RecipeIngredient)
                .options(joinedload(RecipeIngredient.ingredient))
                .where(RecipeIngredient.recipe_id == recipe)
                .where(RecipeIngredient.ingredient_id == ingredient)
            )

            result = session.scalars(stmt).first()

            if result:
                return {
                    "ingredient": result.ingredient,
                    "quantity": result.ingredient_quantity
                }
            else:
                raise NotFoundError("Recipe Ingredient Not Found.")


    def get_all_recipe_ingredients(self,session:Session,recipe:int)->list[dict]:
        try:
            self.get_recipe_by_id(session,recipe)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            result= session.scalars(
                select(RecipeIngredient)
                .options(joinedload(RecipeIngredient.ingredient))
                .where(RecipeIngredient.recipe_id== recipe)).all()
            if result:
                return [{"ingredient": row.ingredient,"quantity": row.ingredient_quantity} for row in result]
            else:
                raise NotFoundError("Recipe Ingredients Not found.")


    def add_recipe_ingredients(self,session:Session,recipe:int,ingredient:int,qty:float)->int| None:
        try:
            self.get_recipe_by_id(session,recipe)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            try:
                self.get_recipe_ingredient(session,recipe,ingredient)
            except NotFoundError:
                recipe_ing=RecipeIngredient(recipe_id=recipe,ingredient_id=ingredient,ingredient_quantity=qty)
                session.add(recipe_ing)
                if self.commit_session(session):
                    return recipe_ing.recipe_ingredients_id
            else:
                raise IntegrityError("Ingredient already exists for the recipe.")

                
            
    
    def update_recipe_qty(self,session:Session,recipe:int,ingredient:int,quantity:float)->int| None:
        try:
            self.get_recipe_by_id(session,recipe)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            recipe_ingredient=session.execute(update(RecipeIngredient)
                .where(RecipeIngredient.recipe_id == recipe)
                .where(RecipeIngredient.ingredient_id == ingredient)
                .values(ingredient_quantity=quantity))
            if not recipe_ingredient:
                raise NotFoundError("Recipe Ingredient Not found.")
            if self.commit_session(session):
                return recipe_ingredient.recipe_ingredients_id

    def delete_recipe_ingredient(self,session:Session,recipe:int,ingredient:int)->int| None:
        try:
            self.get_recipe_by_id(session,recipe)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            recipe_ingredient=session.scalars(select(RecipeIngredient)
                                              .where(RecipeIngredient.recipe_id==recipe)
                                              .where(RecipeIngredient.ingredient_id==ingredient)).first()
            if not recipe_ingredient:
                raise NotFoundError("Recipe Ingredient Not found.")
            session.delete(recipe_ingredient)
            if self.commit_session(session):
                return recipe_ingredient.recipe_ingredients_id

    def delete_all_recipe_ingredients(self,session:Session,recipe:int)->Recipe| None:
        try:
            target_recipe=self.get_recipe_by_id(session,recipe)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            recipe=session.execute(delete(RecipeIngredient).where(RecipeIngredient.recipe_id==recipe))
            if not recipe:
                raise NotFoundError("Recipe Not found.")
            if self.commit_session(session):
                    return target_recipe

    def get_random_recipe(self,session:Session)->Recipe:
        recipes=session.scalars(select(Recipe)).all()
        return random.choice(recipes)

    def get_recipes_from_ingredient(self, session:Session, ingredient_id:int):
        result=session.scalars(select(RecipeIngredient)
        .options(joinedload(RecipeIngredient.recipe))
        .where(RecipeIngredient.ingredient_id == ingredient_id)).all()
        return [value.recipe for value in result]

    def get_common_recipes(self, session, ingredients: set[int]):
        result = (session.scalars(select(Recipe).join(RecipeIngredient)
            .where(RecipeIngredient.ingredient_id.in_(ingredients))
            .group_by(Recipe.recipe_id)
            .having(func.count(RecipeIngredient.recipe_ingredients_id) == len(ingredients)))
        .all())

        return result

    def adjust_recipe_by_servings(self, session:Session,recipe_id:int,servings:int)->dict[Ingredient,float]:
        try:
            recipe=self.get_recipe_by_id(session,recipe_id)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            updated_quantities={}
            recipe_serving=recipe.recipe_servings
            serving_multiplier=(1/recipe_serving)*servings
            recipe_ingredients=self.get_all_recipe_ingredients(session,recipe_id)
            for ingredient in recipe_ingredients:
                recipe_ingredient=ingredient.ingredient
                recipe_quantity=ingredient.quantity
                updated_quantities[recipe_ingredient]=recipe_quantity*serving_multiplier
            return updated_quantities


    def get_recipe_macros(self, session:Session,recipe_id:int,servings:int)->list[float]:
        try:
            recipe=self.get_recipe_by_id(session,recipe_id)
        except NotFoundError as e:
            raise NotFoundError(e)
        else:
            macro_values=[0.0]*4
            recipe_serving=recipe.recipe_servings
            serving_multiplier=(1/recipe_serving)*servings
            recipe_ingredients=self.get_all_recipe_ingredients(session,recipe_id)
            for ingredient in recipe_ingredients:
                macro_ingredient = [ingredient.ingredient_calories,ingredient.ingredient_protein,ingredient.ingredient_fat,ingredient.ingredient_carbs]
                macro_length = len(macro_ingredient)
                for i in range(macro_length):
                    macro_values[i] += round(macro_ingredient[i] *serving_multiplier, 2)
            return macro_values
        

    def generate_meal_plan(self, session:Session,num_recipes:int)->set[Recipe]:
        recipe_list = set()
        if num_recipes <= 0:
            return recipe_list
        first_recipe = self.get_random_recipe(session)
        recipe_list.add(first_recipe)
        current_recipe = first_recipe
        while len(recipe_list) <= num_recipes:
            overlapping_recipes = set()
            recipe_ingredient=self.get_all_recipe_ingredients(session,current_recipe.recipe_id)
            for ingredient in range(len(recipe_ingredient)):
                try:
                    overlapping_recipes.update(self.get_recipes_from_ingredient(session,recipe_ingredient[ingredient]["ingredient"].ingredient_id))
                except ValueError:
                    continue  

            potential_next_recipes = overlapping_recipes - recipe_list
            if not potential_next_recipes:
                all_recipes =self.get_all_recipes(session)
                if not all_recipes:
                    break
                potential_next_recipes = set(all_recipes) - recipe_list

            if not potential_next_recipes:
                break

            next_recipe = random.choice(list(potential_next_recipes))
            recipe_list.add(next_recipe)
            current_recipe = next_recipe
        return recipe_list


    def get_shopping_list(self,session:Session,servings:int, recipe_set:set)-> dict[Ingredient, float]:
        shopping_list = {}
        for recipe in recipe_set:
            ingredients = self.get_all_recipe_ingredients(session,recipe.recipe_id)
            serving_multiplier = (servings / recipe.recipe_servings)

            for ingredient in ingredients:
                ingredient_object = ingredient["ingredient"]
                ingredient_id = ingredient_object.ingredient_id
                if ingredient_id not in shopping_list:
                    shopping_list[ingredient_id] = {"object": ingredient_object, "quantity": 0.0}
                shopping_list[ingredient_id]["quantity"] += ingredient["quantity"] * serving_multiplier

        return shopping_list
