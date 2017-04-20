National Drinking Water Database
--------------------------------

Scrape The Environmental Working Group's [National Drinking Water Database](http://www.ewg.org/tap-water/)


### `zip_codes`

|Name|Type|Description|
|----|----|-----------|
|`zipcode` | `int` | Zip code|
|`city` | `text` | City|
|`state` | `text` | State|
|`lat` | `real` | Latitude|
|`long` | `real` | Longitude|
|...|...|...|

### `suppliers`

Suppliers are entities that supply drinking water

|Name|Type|Description|
|----|----|-----------|
|`id`| `int primary key` | Unique ID|
|`zipcode` | `int` | Zip code the supplier belongs to|
|`suppliers_name` | `text` | Name of the supplier|
|`locations_served` | `text` | Locations served|
|`number_of_people_served` | `int` | Number of people served|
|`href` | `text` | Link to the page containing the information for this supplier|

### `violation_summary`

A summary of the violations.  Each violation is tagged with the `id` of the supplier

|Name|Type|Description|
|----|----|-----------|
|`id` | `int` | `id` of the supplier|
|`violation` | `text` | Description of the violation that took place|
|`date_of_violation` | `text` | Date range for the violation (Ex. `2008/10/01 - 2008/10/31`).  This is likely to be parsed into two separate columns in the future|

### `contaminants`

Fine grained details about contaminations

|Name|Type|Description|
|----|----|-----------|
|`id`|`int` | `id` of the supplier|
|`contaminant` | `text` | Name of the contaminant|
|`average_result` | `text` | Average measurement taken.  This includes the units.  (Ex. `0.14 ppm`)|
|`max_result` | `text` | Maximum measurement taken | 
|`health_limit_exceeded` | `text` | Whether or not the health limit was exceeded|
|`legal_limit_exceeded` | `text` | Whether or not the legal limit was exceeded|