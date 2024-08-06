## Instrcutions

### Install virtualenv with pipenv
1. Check if your environment has pipenv by run pipenv in your termial. if yes, jump to 2.
```sh
brew install pipenv
```
2. Create virtualenv with pipenv and install the packages
2.1. if your project root directory has Pipfile.lock. 
```sh
export PIPENV_VENV_IN_PROJECT=1 && pipenv sync -d
```
if No, run
```sh
export PIPENV_VENV_IN_PROJECT=1 && pipenv shell
```
it will create .venv folder under the root directory.

2.2. then, run 
```sh
source .venv/bin/activate
```
to activate your virtualenv

2.3. run `pipenv install` to install the packages from [packages] and [dev-packages]
2.4. run `pip list` to check if all the necessary python packages have been installed successfuly and correctly.

2.4. (Optional) run `pipenv lock` to create the Pipefile.lock, specificaly, when you have new libraries installed.



references:
* [airflow constraints-3.9](https://raw.githubusercontent.com/apache/airflow/constraints-2.2.5/constraints-3.9.txt)

