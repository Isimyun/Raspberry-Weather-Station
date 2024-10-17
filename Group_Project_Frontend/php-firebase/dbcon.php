<?php   

require __DIR__.'/vendor/autoload.php';

use Kreait\Firebase\Factory;

$factory = (new Factory)
    ->withServiceAccount('group-project-4b008-firebase-adminsdk-q0mh5-628bde33bc.json')
    ->withDatabaseUri('https://group-project-4b008-default-rtdb.firebaseio.com/');

$database = $factory->createDatabase();
?>