from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Recipe


engine = create_engine('sqlite:///recipes.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create initial user to associate recipes
user1 = User(name="Admin Bob", email="admin_bob@gmail.com",
            picture="https://www.publicdomainpictures.net/pictures/270000/velka/apple-piepieicon-sign-food-d.jpg")
session.add(user1)
session.commit()


category1 = Category(user_id=1, name="Breakfast")
breakfast1 = Recipe(user_id=1, name="French Toast",
                    instructions="""Place bread cubes in an instant pot. For
                    chewier French toast, leave the bread out overnight to get
                    slightly stale. Combine all other ingredients in a mixing
                    bowl and whisk to combine. Pour the mixture over the bread
                    cubes in the instant pot and gently toss to ensure
                    everything is evenly coated. Secure the lid and set to cook
                    for 20 minutes. When cooking is complete, release pressure
                    and remove the lid, then transfer the French toast cubes
                    to a serving dish or plates and serve with additional
                    syrup, butter, powdered sugar or whipped cream.""",
                    ingredients="""8 Thick-cut slices of French bread, cubed\r\n
                    2 Eggs\r\n1 Cup milk\r\n2 Teaspoons vanilla extract\r\n2
                    Tablespoons ground cinnamon\r\n½ Teaspoon ground ginger""",
                    category=category1)
breakfast2 = Recipe(user_id=1, name="Chai Pancakes",
                    instructions="""In a large bowl, whisk together the egg,
                    milk, butter, sugar and vanilla. In a separate bowl, stir
                    together cinnamon, cloves, nutmeg, ginger, salt, flour and
                    baking powder. Add the wet to the dry and, using a spatula,
                    mix just until combined. Heat a pan or skillet over medium
                    heat and drop in 1/3 cup of the batter at a time. Flip once
                    when first side is golden brown. Continue until all batter
                    is cooked. Top with maple syrup and serve warm.""",
                    ingredients="""1 Egg\r\n1 ¼ Cup milk\r\n3 Tablespoons melted
                    butter\r\n1 Tablespoon sugar\r\n 1 Teaspoon vanilla\r\n1
                    Teaspoon cinnamon\r\n½ Teaspoon ground cloves\r\n½ Teaspoon
                    ground nutmeg\r\n½ Teaspoon ground ginger\r\n1 Teaspoon
                    salt\r\n1 ½ Cups flour\r\n3 ½ Teaspoons baking powder""",
                    category=category1)
breakfast3 = Recipe(user_id=1, name="Breakfast Egg Muffins",
                    instructions="""Whisk together the eggs in a large bowl. Add
                    the salt, pepper, garlic powder, onion, green pepper, bacon,
                    and Cheddar and combine all ingredients. Line a muffin tin
                    with paper liners (these egg muffins love to stick even with
                    spray, so liners work best). Spoon the mixture into each
                    cup of the muffin tin; fill approximately ¾ full as these
                    will puff up as they cook. Bake in a 350 degree oven for
                    about 20 minutes or until set. Serve hot.""",
                    ingredients="""12 eggs\r\n¼ teaspoon pepper\r\n½ teaspoon salt
                    \r\n½ teaspoon garlic powder\r\n½ an onion, chopped\r\n½ of
                    a green pepper, chopped\r\n½ cup cooked bacon, chopped\r\n
                    4 ounces Cheddar cheese, shredded""",
                    category=category1)

category2 = Category(user_id=1, name="Appetizers")
appetizer1 = Recipe(user_id=1, name="Avocado Fries with Lime Dipping Sauce",
                    instructions="""Preheat the oven 425F, follow directions
                    above and bake on a sheet pan until golden and crisp, 10 to
                    15 minutes. Place egg in a shallow bowl. On another plate,
                    combine panko with 1 teaspoon Tajin. Season avocado wedges
                    with 1/4 teaspoon Tajin.  Dip each piece first in egg, and
                    then in panko. Spray both sides with oil then transfer to
                    the air fryer and cook 7 to 8 minutes turning halfway.
                    Serve hot with dipping sauce.""",
                    ingredients="""8 ounces (2 small) avocados, peeled, pitted
                    and cut into 16 wedges\r\n1 large egg, lightly beaten\r\n
                    3/4 cup panko breadcrumbs (I used gluten-free)\r\n1 1/4
                    teaspoons lime chili seasoning salt, such as Tajin Classic
                    \r\nFor the lime dipping sauce:\r\n1/4 cup 0% Greek Yogurt
                    \r\n3 tablespoons light mayonnaise\r\n2 teaspoons fresh
                    lime juice\r\n1/2 teaspoon lime chili seasoning salt, such
                    as Tajin Classic\r\n1/8 teaspoon kosher salt""",
                    category="category2")
