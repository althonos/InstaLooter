<!-- Below you'll find a template to create an issue, with information you're
expected to provide to help debugging. Failure to do so will most likely
end up in your issue being ignored. Let's try being adults here, an issue
named IT DOESN'T WORK without a description is not helping anybody. -->

## Library version

*What's the installed library version ? Check with `instalooter --version`*:

```
instalooter vX.Y.Z
```

## Environment

*Describe here your environment, including:*

* *OS*
* *Python version*
* *`setuptools` version if reporting an issue with installation*
* *non-standard Python implementation if any*


## Error description - installation

*If you have an issue with installation, make sure you use a recent `setuptools` version
before filing a bug ! If the error is still there, describe the command you used to
install, and make sure you reported your environment in details. In particular,
if you encounter a critical error with the CLI, please post the program output when
running with the `--traceback` flag.*


## Error description - runtime

*If you have an issue at runtime, include the required information below:*

### Reproducible test case

*Are you using the CLI ? If so, include a command that can be used to re-raise the
error, with actual arguments anybody can try:*

```
instalooter ...
```

*Are you using the API ? If so, include a small snippet that can be used to re-raise the
error:*

```python
from instalooter.looters import ...
```


### Expected behaviour

*What's supposed to happen ? That's were you can ask for a new feature as well*

### Actual behaviour

*What's actually happening ? Leave empty if asking for a new feature*
