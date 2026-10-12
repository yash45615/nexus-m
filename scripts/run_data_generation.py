from scripts.generate_dimensions import main as generate_dimensions
from scripts.generate_transactions import generate_transactions
from scripts.generate_settlements import generate_settlements
from scripts.generate_partner_events import generate_partner_events


def main():

    print("=" * 80)
    print("NEXUS-M COMPLETE SYNTHETIC DATA GENERATION")
    print("=" * 80)

    print("\n[1/4] Generating dimensions...")
    generate_dimensions()

    print("\n[2/4] Generating transactions...")
    generate_transactions()

    print("\n[3/4] Generating settlements...")
    generate_settlements()

    print("\n[4/4] Generating partner events...")
    generate_partner_events()

    print("\n" + "=" * 80)
    print("NEXUS-M DATA GENERATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()