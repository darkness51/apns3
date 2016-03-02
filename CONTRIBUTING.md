# Contributing
## TL;DR
It's pretty simple:

1. Make some changes
2. Check your code style with `make flake8`
3. Write some tests
4. Run your tests with `make run`
5. Update the docs if neccesary

## Tests
To run the test suite:

```
$ make test
```

Coverage will be reported to the console. You can also view an HTML formatted
coverage report with:

```
$ make htmlcov
```

## Style Checks
This project uses the `flake8` tool to keep the source code in line with PEP8
reccomentations. Run the checker with:

```
$ make flake8
```

## Documentation
Build the Sphinx docs with:

```
$ make doc
```

Open the generated docs in your browser to check them:

```
$ make read
# opens docs/build/html/index.html
```
