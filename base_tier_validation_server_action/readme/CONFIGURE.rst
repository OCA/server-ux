On each Tier Definition

* Choose server action you want to call as soon this definition is validated
* Select "Auto Validate", if you want this definition to get validated by cron job based on "if pass condition" criteria,
   * If no user specified, use job's system user to validate
   * If 1 user matched as reviewer, use the user to validate
   * If > 1 user matched as reviewer, do not auto validate
