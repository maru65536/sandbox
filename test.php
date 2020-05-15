<?php
    $pdo = new PDO('mysql:host=172.17.196.154;dbname=test;charset=utf8','root','3412');
    $qry = $pdo->prepare('select * from test');
    $qry->execute();
    foreach ($qry->fetchAll() as $q) {
        echo $q['id'];
    }
?>