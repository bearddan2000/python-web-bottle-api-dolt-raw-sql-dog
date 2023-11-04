from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.sql import text

class Raw():
    def __init__(self, db: sessionmaker) -> None:
        self.db = db

    def jsonify_results(self, collection: CursorResult) -> dict:
        results = [
            {
                "id": item.id,
                "breed": item.breed,
                "color": item.color
            } for item in collection]

        return {"results": results}
    
    def all(self):
        collection = self.db.execute(text("SELECT * FROM dog"))
        return self.jsonify_results(collection)

    def commit_refresh(self, args: dict, stm) -> dict:
        self.db.execute(statement=stm,params=args)
        self.db.commit()
        return self.all()

    def filter_by(self, dog_id: int):
        stm = text("SELECT * FROM dog WHERE id = :dog_id")
        collection = self.db.execute(statement=stm,params={"dog_id": int(dog_id)})
        return self.jsonify_results(collection)

    def delete_by(self, dog_id: int):
        stm = text("DELETE FROM dog WHERE id = :dog_id")
        return self.commit_refresh(args={"dog_id": int(dog_id)}, stm=stm)
    
    def insert_entry(self, dog_breed: str, dog_color: str):
        stm = text("SELECT * FROM dog WHERE id = (SELECT MAX(id) FROM dog)")
        collection = self.db.execute(statement=stm)
        results = self.jsonify_results(collection)
        dog_id = int(results['results'][0]['id']) + 1
        args = {"dog_id": dog_id, "dog_breed": dog_breed, "dog_color": dog_color}
        stm = text("INSERT INTO dog(id, breed, color) VALUES(:dog_id, :dog_breed, :dog_color)")
        return self.commit_refresh(args=args, stm=stm)

    def update_entry(self, dog_id: int, dog_breed: str, dog_color: str):
        args = {"dog_id": dog_id, "dog_breed": dog_breed, "dog_color": dog_color}
        stm = text("UPDATE dog SET breed=:dog_breed, color=:dog_color WHERE id=:dog_id")
        return self.commit_refresh(args=args, stm=stm)
