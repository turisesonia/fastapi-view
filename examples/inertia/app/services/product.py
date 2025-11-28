from typing import List

from app.schemas.product import ProductSchema


class ProductService:
    """商品業務邏輯服務"""
    
    def get_all_products(self) -> List[ProductSchema]:
        """取得所有商品列表"""
        products = []
        for n in range(1, 6):
            product = ProductSchema(
                id=n,
                name=f"商品-{n}",
                price=n * 10,
                description=f"這是商品 {n} 的詳細描述",
                image=f"https://api.lorem.space/image/game?w=150&h=220&id={n}"
            )
            products.append(product)
        return products
    
    def get_product_by_id(self, product_id: int) -> ProductSchema:
        """根據 ID 取得單個商品"""
        return ProductSchema(
            id=product_id,
            name=f"商品-{product_id}",
            price=product_id * 10,
            description=f"這是商品 {product_id} 的詳細描述",
            image=f"https://api.lorem.space/image/game?w=300&h=400&id={product_id}"
        )
    
    def get_featured_products(self, limit: int = 3) -> List[ProductSchema]:
        """取得精選商品"""
        all_products = self.get_all_products()
        return all_products[:limit]