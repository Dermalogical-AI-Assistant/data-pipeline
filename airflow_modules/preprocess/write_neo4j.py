from common.constant import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from preprocess.utils import convert_obj_to_string
from neo4j import GraphDatabase
import json

class Neo4jConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, 
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
            max_connection_lifetime=3600,
            connection_timeout=30
        )
    
    def close(self):
        self.driver.close()
    
    def create_product_graph(self, product_data):
        with self.driver.session() as session:
            # Create Product node
            session.write_transaction(self._create_product_node, product_data)
            
            analysis = product_data.get('ingredients_analysis')
            print(f'analysis = {json.dumps(analysis, indent=4)}')

            # Create Ingredients and Relationships
            if analysis and isinstance(analysis, dict) :
                session.write_transaction(self._process_ingredients, product_data['url'], analysis)
    
    @staticmethod
    def _create_product_node(tx, product):
        ingredients_analysis = product.get('ingredients_analysis', {})
        if isinstance(ingredients_analysis, dict) == False:
            ingredients_analysis = {}
        
        MERGE_PRODUCT_QUERY = """
            MERGE (p:Product {url: $url})
            SET p._id = $_id,
                p.img = $img,
                p.title = $title,
                p.price = $price,
                p.skincare_concern = apoc.coll.toSet(COALESCE(p.skincare_concern, []) + $skincare_concern),
                p.description = $description,
                p.how_to_use = $how_to_use,
                p.ingredient_benefits = $ingredient_benefits,
                p.full_ingredients_list = $full_ingredients_list,
                p.ewg = $ewg,
                p.natural = $natural,
                p.analysis_text = $analysis_text,
                p.analysis_description = $analysis_description
        """     
        tx.run(MERGE_PRODUCT_QUERY, 
            _id=product['_id'],
            img=product['img'],
            title=product['title'],
            price=product['price'],
            url=product['url'],
            skincare_concern=product['skincare_concern'],
            description=product['description'],
            how_to_use=product['how_to_use'],
            ingredient_benefits=product['ingredient_benefits'],
            full_ingredients_list=product['full_ingredients_list'],
            ewg=convert_obj_to_string(ingredients_analysis.get('ewg')),
            natural=convert_obj_to_string(ingredients_analysis.get('natural')),
            analysis_text=ingredients_analysis.get('text', None),
            analysis_description=ingredients_analysis.get('description', '')
        )
    
    @staticmethod
    def _process_ingredients(tx, product_url, analysis):
        for ingredient in analysis.get('ingredients_table', []):
            MERGE_INGREDIENT_QUERY = """
                MERGE (i:Ingredient {id: $id})
                SET i.title = $title,
                    i.cir_rating = $cir_rating,
                    i.introtext = $introtext,
                    i.categories = $categories,
                    i.properties = $properties,
                    i.integer_properties = $integer_properties,
                    i.ewg = $ewg
            """
            tx.run(MERGE_INGREDIENT_QUERY,
                id=ingredient['id'],
                title=ingredient['title'],
                cir_rating=ingredient['cir_rating'],
                introtext=ingredient['introtext'],
                categories=ingredient['categories'],
                properties=ingredient['properties'],
                integer_properties=convert_obj_to_string(ingredient['integer_properties']),
                ewg=convert_obj_to_string(ingredient['ewg'])
            )
            
            # Create HAS relationship between Product and Ingredient
            CREATE_HAS_RELATIONSHIP_QUERY = """
                MATCH (p:Product {url: $product_url})
                MATCH (i:Ingredient {id: $ingredient_id})
                MERGE (p)-[r:HAS]->(i)
                SET r.updated_at = timestamp()
            """
            tx.run(CREATE_HAS_RELATIONSHIP_QUERY,
                product_url=product_url,
                ingredient_id=ingredient['id']
            )
        
        # Create HARMFUL relationships
        for harm_type, harm_data in analysis.get('harmful', {}).items():
            for item in harm_data.get('list', []):
                CREATE_HARMFUL_RELATIONSHIP_QUERY = """
                    MATCH (p:Product {url: $product_url})
                    MATCH (i:Ingredient {title: $ingredient_title})
                    OPTIONAL MATCH (p)-[existing:HARMFUL]->(i)
                    WHERE existing.title = $title
                    FOREACH (_ IN CASE WHEN existing IS NULL THEN [1] ELSE [] END |
                        CREATE (p)-[:HARMFUL {
                        title: $title,
                        type: $type,
                        description: $description,
                        updated_at: timestamp()
                        }]->(i)
                    )
                """
                tx.run(CREATE_HARMFUL_RELATIONSHIP_QUERY,
                    product_url=product_url,
                    ingredient_title=item['title'],
                    type=harm_type,
                    title=harm_data['title'],
                    description=harm_data['description']
                )
        
        # Create POSITIVE relationships 
        for pos_type, pos_data in analysis.get('positive', {}).items():
            for item in pos_data.get('list', []):
                CREATE_POSITIVE_RELATIONSHIP_QUERY = """
                    MATCH (p:Product {url: $product_url})
                    MATCH (i:Ingredient {title: $ingredient_title})
                    OPTIONAL MATCH (p)-[existing:POSITIVE]->(i)
                    WHERE existing.title = $title
                    FOREACH (_ IN CASE WHEN existing IS NULL THEN [1] ELSE [] END |
                        CREATE (p)-[:POSITIVE {
                        title: $title,
                        type: $type,
                        description: $description,
                        updated_at: timestamp()
                        }]->(i)
                    )
                """
                tx.run(CREATE_POSITIVE_RELATIONSHIP_QUERY,
                    product_url=product_url,
                    ingredient_title=item['title'],
                    type=pos_type,
                    title=pos_data['title'],
                    description=pos_data['description']
                )
        
        # Create NOTABLE relationships
        for notable_type, notable_data in analysis.get('notable', {}).items():
            for item in notable_data.get('list', []):
                CREATE_NOTABLE_RELATIONSHIP_QUERY = """
                    MATCH (p:Product {url: $product_url})
                    MATCH (i:Ingredient {title: $ingredient_title})
                    OPTIONAL MATCH (p)-[existing:NOTABLE]->(i)
                    WHERE existing.title = $title
                    FOREACH (_ IN CASE WHEN existing IS NULL THEN [1] ELSE [] END |
                        CREATE (p)-[:NOTABLE {
                        title: $title,
                        type: $type,
                        updated_at: timestamp()
                        }]->(i)
                    )
                """
                tx.run(CREATE_NOTABLE_RELATIONSHIP_QUERY,
                    product_url=product_url,
                    ingredient_title=item['title'],
                    type=notable_type,
                    title=notable_data['title']
                )

def write_product_to_neo4j(product):
    neo4j = Neo4jConnector()

    product_data = {
        "_id": product["_id"],
        "img": product["img"],
        "title": product["title"],
        "price": product["price"],
        "url": product["url"],
        "skincare_concern": product["skincare_concern"],
        "description": product["description"],
        "how_to_use": product["how_to_use"],
        "ingredient_benefits": product["ingredient_benefits"],
        "full_ingredients_list": product["full_ingredients_list"],
        "ingredients_analysis": product["ingredients_analysis"]
    }

    neo4j.create_product_graph(product_data)
    
    neo4j.close()
    