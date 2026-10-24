# Architecture

Use the [architecture document](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/ARCHITECTURE.md) for
accepted technical boundaries. The
[modularisation plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/MODULARISATION_PLAN.md) explains
module responsibilities and the direction of dependencies.

## A guide to the layers

| Layer | What to look for |
| --- | --- |
| Domain | Railway records, calculations, identities and rules |
| Application | Commands, workflow orchestration and contracts |
| FreeCAD adapters | Document persistence, transactions and exact geometry |
| Presentation | Derived display and mapping selections to railway identities |
| Export adapters | Format preparation, staging and output |
| UI and compatibility | Interaction with application commands and explicit legacy concerns |

This table is a reading aid. The source documents define the full boundaries
and their exceptions. Their target source layout is a responsibility map;
it does not mean that every proposed component is already implemented.

## Follow a change through the code

Begin with the relevant capability and its evidence in the
[capability matrix](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/CAPABILITY_MATRIX.md).
Then locate the contract in
[`tracktemplate/api.py`](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/tracktemplate/api.py) and follow its
implementation into the owning module.

The façade is part of a development checkpoint. Treat a symbol's source
presence separately from a claim that it is a stable released API.

The [product vision](https://github.com/Richard-Gnitnub/tracktemplate/blob/54c5903b41e89d1fdfb430c812495e36b91d690b/reference/PRODUCT_VISION.md) distinguishes
the current Core migration from the later Layout Editor direction.
For what has been accepted now, follow the
[live project plan](https://github.com/Richard-Gnitnub/tracktemplate/blob/main/reference/PROJECT_PLAN.md).
