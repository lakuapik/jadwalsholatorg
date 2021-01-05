<?php

/**
 * Previously, the repo has daily json file.
 * But overtime, it has lot of files and got bigger size.
 * It makes the git run slowly. So i decided to just delete it.
 */

function scan(string $dir): array
{
    return array_filter(scandir($dir), fn ($d) => !in_array($d, ['.', '..']));
}

// https://stackoverflow.com/a/7288067
function rmdir_recursive($dir): void
{
    foreach (scandir($dir) as $file) {
        if ('.' === $file || '..' === $file) continue;
        if (is_dir("$dir/$file")) rmdir_recursive("$dir/$file");
        else unlink("$dir/$file");
    }
    rmdir($dir);
}

foreach (scan('./../adzan/') as $dir) {
    foreach (scan("./../adzan/{$dir}/") as $dirx) {
        foreach (scan("./../adzan/{$dir}/{$dirx}") as $diry) {
            $finalDir = "./../adzan/{$dir}/{$dirx}/{$diry}";
            if (is_dir($finalDir)) {
                rmdir_recursive($finalDir);
            }
        }
    }
}
