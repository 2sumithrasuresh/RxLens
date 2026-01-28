import csv
import sys
from pathlib import Path

def esc(value: str) -> str:
    return value.replace("'", "''")

def is_number(val: str) -> bool:
    try:
        float(val)
        return True
    except ValueError:
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python csv_to_sql.py <path/to/file.csv>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])

    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        sys.exit(1)

    table_name = csv_path.stem

    output_dir = Path("database")
    output_dir.mkdir(exist_ok=True)

    output_sql = output_dir / f"{table_name}.sql"

    with open(csv_path, newline="", encoding="utf-8") as f, \
         open(output_sql, "w", encoding="utf-8") as out:

        reader = csv.DictReader(f)
        columns = reader.fieldnames

        if not columns:
            print("CSV has no headers")
            sys.exit(1)

        out.write("START TRANSACTION;\n")
        out.write("USE rxlens;\n\n")

        col_list = ", ".join(columns)

        for row in reader:
            values = []
            for col in columns:
                val = row[col]

                if val is None or val == "":
                    values.append("NULL")
                elif is_number(val):
                    values.append(val)
                else:
                    values.append(f"'{esc(val)}'")

            values_sql = ", ".join(values)

            out.write(
                f"INSERT IGNORE INTO {table_name} ({col_list}) "
                f"VALUES ({values_sql});\n"
            )

        out.write("\nCOMMIT;\n")

    print(f"✅ Generated {output_sql}")

if __name__ == "__main__":
    main()
