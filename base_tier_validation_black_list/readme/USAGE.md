A clear use case is when multiple modules are expected to be installed.
This will create fields in various models, such as sales or purchase orders.
To avoid exhaustive maintenance, instead of adding exceptions to allow editing,
we add exceptions for the fields that will not be edited.
