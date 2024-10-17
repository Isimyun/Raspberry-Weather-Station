<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="styling.css">
</head>

<body>

    <?php
    session_start();
    ?>
    
    <div style="margin-left:50px;margin-right:50px;">

        <table>
            <thead>
                <h1>Weather Station</h1>
                <tr>
                    <th>Measurements</th>
                    <th>Humidity</th>
                    <th>Temperature</th>
                    <th>Pressure</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                <?php
                include 'dbcon.php';

                $ref_table = 'measurement';
                $fetchdata = $database->getReference($ref_table)->getValue();

                if ($fetchdata > 0) {
                    $i = 1;
                    foreach ($fetchdata as $key => $row) {
                        ?>
                        <tr>
                            <td>
                                <?= $i++; ?>
                            </td>
                            <td>
                                <?= $row['humidity']; ?>
                            </td>
                            <td>
                                <?= $row['temperature']; ?>
                            </td>
                            <td>
                                <?= $row['pressure']; ?>
                            </td>
                            <td>
                                <?= $row['timestamp']; ?>
                            </td>
                        </tr>
                        <?php
                    }
                } else {
                    ?>
                    <tr>
                        <td>No Record Found</td>
                    </tr>
                    <?php
                }
                ?>
                
            </tbody>
        </table>
    </div>
    
</body>

</html>