#!/usr/bin/env python
import argparse
from pathlib import Path
from typing import List, Tuple
from melbalabs.summarize_consumes.consumable_model import PriceComponent
from melbalabs.summarize_consumes.consumable_model import DirectPrice
from melbalabs.summarize_consumes.consumable_model import PriceFromIngredients
from melbalabs.summarize_consumes.consumable_db import all_defined_consumable_items
from melbalabs.summarize_consumes.entity_model import Entity, get_entities_with_component

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()

    with open(args.output_path, "w", newline='\n') as f:
        f.write("| Consumable | Price | Charges |\n")
        f.write("|------------|--------|----------|\n")

        data : List[Tuple[Entity, PriceComponent]] = []

        for consumable, price_info in get_entities_with_component(PriceComponent):
            data.append((consumable, price_info))

        data.sort(key=lambda x: x[0].name)

        for consumable, price_info in data:
            price_str = ""
            charges_str = ""
            if isinstance(price_info.price, DirectPrice):
                itemid = price_info.price.itemid
                price_str = f"[{itemid}](https://database.turtle-wow.org/?item={itemid})"
                if price_info.price.charges > 1:
                    charges_str = str(price_info.price.charges)
            elif isinstance(price_info.price, PriceFromIngredients):
                ingredients = []
                for ingredient, count in price_info.price.ingredients:
                    ingredients.append(f"{count} x {ingredient.name}")
                price_str = "<br>".join(ingredients)
                if price_info.price.charges > 1:
                    charges_str = str(price_info.price.charges)

            f.write(f"| {consumable.name} | {price_str} | {charges_str} |\n")

if __name__ == "__main__":
    main()
