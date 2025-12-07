#!/usr/bin/env python
import argparse
from pathlib import Path
from melbalabs.summarize_consumes.consumable_model import DirectPrice
from melbalabs.summarize_consumes.consumable_model import PriceFromIngredients
from melbalabs.summarize_consumes.consumable_db import all_defined_consumable_items

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()

    with open(args.output_path, "w", newline='\n') as f:
        f.write("| Consumable | Price | Charges |\n")
        f.write("|------------|--------|----------|\n")

        for consumable in sorted(all_defined_consumable_items, key=lambda x: x.name):
            price_str = ""
            charges_str = ""

            if isinstance(consumable.price, DirectPrice):
                price_str = f"[{consumable.price.itemid}](https://database.turtle-wow.org/?item={consumable.price.itemid})"
                if consumable.price.charges > 1:
                    charges_str = str(consumable.price.charges)
            elif isinstance(consumable.price, PriceFromIngredients):
                components = []
                for component, count in consumable.price.ingredients:
                    components.append(f"{count} x {component.name}")
                price_str = "<br>".join(components)
                if consumable.price.charges > 1:
                    charges_str = str(consumable.price.charges)

            f.write(f"| {consumable.name} | {price_str} | {charges_str} |\n")

if __name__ == "__main__":
    main()
