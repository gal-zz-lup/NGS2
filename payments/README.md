# World Labs Incentive Payment Processing
## Introduction
As part of World Labs, Gallup will be sending participants their incentive payments via [PayPal](https://www.paypal.com). This is an easy, convenient, and inexpensive way to transfer payments to participants around the world quickly.

To assist in these payments, Gallup uses the [PayPal APIs](https://developer.paypal.com) to facilitate payments in bulk. This repository contains the code to help facilitate the transfer of those payments to participants.

## Setup
Specifically, this repository uses the [Payouts API](https://developer.paypal.com/docs/api/payments.payouts-batch) from PayPal, which allows a user to transfer up to 250 payments in a single API call. To do this requires a few pieces of information:

1. A .csv or .txt file with details on the payments to process
2. A developer account
3. REST API keys to authenticate against the API

In addition, this repository is using PayPal's official [Python SDK](https://github.com/paypal/PayPal-Python-SDK) to authenticate and make API calls.

### Payment details
A required piece of information for processing payments is an input worksheet as either a .csv or .txt file. **For purposes here, a .csv file is required.** The .csv should have the following fields:

#### Required Fields
* `batch_id`:
    * Field type: Alphanumeric string
    * Description: Determined by Gallup; will identify which participants are batched together for payment.
    * Notes: There can be no more than 250 participants in a single batch. This will be checked at run-time by the program and the program will abort if a batch has more than 250 participants in it.
* `first_name`:
    * Field type: String
    * Description: This is the participant's first name as provided at empanelment.
    * Notes: This field is used to customize the email message accompanying the PayPal payment.
* `receiver_email`:
    * Field type: Email address
    * Description: This is the participant's email address as provided at empanelment.
    * Notes: This is the email address at which they'll receive payment. If the participant does not have a PayPal account, they can open one with this email. If they do have a PayPal account, but with another email address, they will be able to link their payment from this email address to their existing account.
* `value`:
    * Field type: Float
    * Description: The value of the participant's payment.
    * Notes: This value should be in decimal format, with no more than two decimal points. **Do not add any additional characters like $ or , to this field.**
* `currency`:
    * Field type: String
    * Description: The type of currency associated with the `value` amount.
    * Notes: Currency, this can be `USD` (for U.S. dollars) or `PHP` (for Philippine Pesos). All other currency choices will cause the program to abort.
* `item_id`:
    * Field type: Alphanumeric string
    * Description: This is the individual identifying transaction code within a batch
    * Notes: This is determined by Gallup for recordkeeping purposes.
* `processed_code`:
    * Field type: Alphanumeric string
    * Description: *This field will be blank for transactions that have not been processed* and will be filled in when the program executes
    * Notes: This field is to record the PayPal transaction processing code in case follow-up after-the-fact is needed. **In the input worksheet, this field must be blank**; if it is not, then the transaction will not be processed.

#### Worksheet examples
An example of what the input worksheet will look like before processing is below (note, the `processed_code` column is blank):

batch_id | first_name | receiver_email | value | currency | item_id | processed_code
--- | --- | --- | --- | --- | --- | ---
AAA | Bob | bob@notrealemail.com | 0.12 | USD | AAA001 |
AAA | Rob | rob@notrealemail.com | 1.23 | USD | AAA002 |
BBB | Sob | sob@notrealemail.com | 0.99 | USD | BBB001 |

After the program processes the payments, the same worksheet will look like the example below (note, the `processed_code` for a `batch_id` is identical):

batch_id | first_name | receiver_email | value | currency | item_id | processed_code
--- | --- | --- | --- | --- | --- | ---
AAA | Bob | bob@notrealemail.com | 0.12 | USD | AAA001 | S0MECODE
AAA | Rob | rob@notrealemail.com | 1.23 | USD | AAA002 | S0MECODE
BBB | Sob | sob@notrealemail.com | 0.99 | USD | BBB001 | @DIFFCODE

#### What to do
There will be one input worksheet that will serve as a general 'ledger' of payment transactions throughout the life of World Labs. The worksheet will have all required fields as listed above, and as transactions are entered for payment/processing, all details *other than* the `processed_code` will be filled in. Once the ledger is processed, then a PayPal processing code will be added to the entry. In this way, one ledger can be used over and over, as the payout program will only look for transactions that **do not have** a `processed_code`, since that indicates the transaction is 'new' and needs to be processed.

## Running the program
The processing program is written in Python and can be called from the command line. It takes three required arguments:

* `-a` or `--auth`: **This argument requires two inputs.** The first is the PayPal REST API key for the account sending money and the second is the PayPal REST API secret. These are assigned by PayPal when an application using its REST APIs is created.
* `-e` or `--environment`: This argument is either `sandbox` or `production`. All other arguments will cause the program to abort. For actual payments, `production` should be used; using `sandbox` will allow one to test if the transactions are structured correctly, but it will not make an actual payment.
* `-p` or `--payments`: This is the full path and file name to the .csv that contains payment transaction information. This file is both input and output; once read in and payments are processed, this file will be updated by adding the `processed_code` to each transaction and writing it back to disk.

### Command-line Execution
To execute the program, below is an example call:

```
$ python payments/paypal.py -a $PAYPAL_ID $PAYPAL_SECRET \
                            -e sandbox \
                            -p ~/Documents/ngs2/example_payouts.csv
```

where `$PAYPAL_ID` and `$PAYPAL_SECRET` are stored environmental variables with the appropriate REST API key/secret values. This call is executing against the `sandbox` API (meaning no money is actually transferred) and the payment transaction .csv path/file is fully specified.

### Logging
The payment program is set up with logging. Logging is important in being able to have a record of each time the program is run and what actually happened during the execution. The logging file is called `paypal_processing.log` and stored in the `payments` folder of the repository. Each execution of the program will *append* to the log, not overwrite the last transaction, meaning a complete record of all executions is possible to have on disk.

### Testing
This program includes a set of tests for the various functions that are being called through execution. They should be kept up-to-date as program functions change.

## Troubleshooting
If there are questions or problems, contact [Matt Hoover](matt_hoover@gallup.com) for assistance.

## Conclusion
This payment program is a simple execution of bulk payouts using the PayPal APIs and SDK. If needed, it can be expanded upon and used for other means. In addition, work to automate the population of the input worksheet should be undertaken as soon as the schema for how those data will be accessed is determined.
