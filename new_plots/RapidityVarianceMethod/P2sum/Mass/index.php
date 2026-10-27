<?php
  // author: Marcel Rieger
  // see https://gitlab.cern.ch/cms-analysis/general/php-plots for more info

  //
  // settings
  //

  // extension of files to show in cards
  $main_extension = "pdf";

  // additional extensions to link in card footer
  $additional_extensions = array(
    "pdf", "png", "jpg", "jpeg", "gif", "eps", "svg", "root", "cxx", "txt", "rtf", "log", "csv",
  );

  // search mode in case multiple search strings are used
  // any: any search pattern must match
  // all: all search patterns must match
  // exact: the search pattern must match as is
  // in all modes, the case is ignored and bins written as e.g. "Pt_0_1" and "pt0-1" are treated alike
  $search_pattern_mode = "any";


  //
  // helpers
  //

  // function that checks whether a search pattern is contained in a name, ignoring the case and the
  // different ways of writing bins: "_" and "-" are interchangeable and optional between letters and
  // numbers, while numbers must match whole numbers, also next to a "*", so that "Pt_0_1" and
  // "Pt_0_1*" match "pt0-1" but not "pt0-10"; "*" and "?" are wildcards as before
  function match_pattern($pattern, $name) {
    $chars = str_split($pattern);
    $regex = "";
    foreach ($chars as $i => $c) {
      $prev = ($i > 0) ? $chars[$i - 1] : "";
      $next = ($i < count($chars) - 1) ? $chars[$i + 1] : "";
      if ($c == "_" || $c == "-") {
        $optional = (ctype_alpha($prev) && ctype_digit($next)) || (ctype_digit($prev) && ctype_alpha($next));
        $regex .= $optional ? "[_-]?" : "[_-]";
      } else if ($c == "*") {
        $regex .= ".*";
      } else if ($c == "?") {
        $regex .= ".";
      } else {
        // a number must not continue a number in the name where the pattern does not limit it
        if (ctype_digit($c) && ($prev == "" || $prev == "*")) {
          $regex .= "(?<![0-9.])";
        }
        $regex .= preg_quote($c, "/");
        if (ctype_digit($c) && ($next == "" || $next == "*")) {
          $regex .= "(?!\.?[0-9])";
        }
        // a letter directly followed by a number, or vice versa, may also be written with a separator
        if ((ctype_alpha($c) && ctype_digit($next)) || (ctype_digit($c) && ctype_alpha($next))) {
          $regex .= "[_-]?";
        }
      }
    }
    return preg_match("/$regex/i", $name) == 1;
  }

  // function that checks whether a search pattern matches an entry given by its path, using the path
  // relative to the top directory when the pattern contains a "/", e.g. "*/Raw/*Pt_0_1*", and only
  // the name of the entry otherwise
  function match_entry($pattern, $path) {
    $subject = (strpos($pattern, "/") === False) ? basename($path) : "/" . display_path($path);
    return match_pattern($pattern, $subject);
  }

  // function that decides whether an entry given by its path is shown,
  // considering its name and optional search strings
  function show_entry($path) {
    global $search_pattern_mode;
    $name = basename($path);

    // always hide entries starting with "." or "_"
    if (substr($name, 0, 1) == "." || substr($name, 0, 1) == "_") {
      return False;
    }

    // show the entry when no search pattern is defined
    if (!isset($_GET["search"]) || empty($_GET["search"])) {
      return True;
    }

    // split into subpatterns by space
    $patterns = explode(" ", preg_replace("/\s+/", " ", $_GET["search"]));

    if ($search_pattern_mode == "all") {
      // all patterns must match
      foreach($patterns as $pattern) {
        if (!match_entry($pattern, $path)) {
          return False;
        }
      }
      return True;

    } else if ($search_pattern_mode == "any") {
      // at least one pattern must match
      foreach($patterns as $pattern) {
        if (match_entry($pattern, $path)) {
          return True;
        }
      }
      return False;

    } else {
      // match with the search pattern as is
      return match_entry($_GET["search"], $path);
    }
  }

  // a search always looks into all directories of the plot browser, starting from its top
  $search_recursive = isset($_GET["search"]) && !empty($_GET["search"]);

  // function that returns the relative path to the top directory of the plot browser, derived from
  // the number of directories in the requested url (the web server might not be allowed to look at
  // anything above the top directory, so the file system cannot be used for that)
  function find_top_dir() {
    $url_path = parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH);
    // remove a trailing file name such as index.php
    $url_path = substr($url_path, 0, strrpos($url_path, "/"));
    $depth = count(array_filter(explode("/", $url_path), "strlen"));
    // do not go above the top directory, e.g. when the site is served below some url prefix
    while ($depth > 0 && !is_file(str_repeat("../", $depth) . "index.php")) {
      $depth--;
    }
    return ($depth == 0) ? "." : rtrim(str_repeat("../", $depth), "/");
  }

  $top_dir = $search_recursive ? find_top_dir() : ".";

  // function that returns a path relative to the top directory, used for displaying it
  function display_path($path) {
    global $top_dir;
    return ($top_dir == ".") ? $path : substr($path, strlen($top_dir) + 1);
  }

  // function that returns the relative paths of all entries in a directory, and of those in its
  // subdirectories when searching recursively, without descending into hidden or linked ones
  $n_searched_dirs = 0;
  function list_entries($dir = ".") {
    global $search_recursive, $n_searched_dirs;

    $n_searched_dirs++;
    $paths = array();
    foreach (scandir($dir) as $name) {
      if ($name == "." || $name == "..") {
        continue;
      }
      $path = ($dir == ".") ? $name : "$dir/$name";
      array_push($paths, $path);
      $hidden = substr($name, 0, 1) == "." || substr($name, 0, 1) == "_";
      if ($search_recursive && !$hidden && is_dir($path) && !is_link($path)) {
        $paths = array_merge($paths, list_entries($path));
      }
    }
    return $paths;
  }

  $entries = list_entries($top_dir);
?>

<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- include third-party style sheets via cdns -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">

    <!-- minimal custom styles -->
    <style type="text/css">
      a {
        text-decoration: none;
      }

      nav ol.breadcrumb {
        margin: 0;
        padding: 0;
        background-color: transparent;
      }

      body > div.container-fluid {
        margin: 15px 0;
        padding: 0 15px;
      }

      .empty-text {
        font-style: italic;
        font-size: 0.9rem;
      }

      #plot-listing .card {
        margin: 5px;
      }

      #plot-listing .plot-group {
        margin: 20px 5px 5px;
      }

      #plot-listing .card-header {
        font-size: 0.8rem;
        padding: 0.4rem;
      }

      #plot-listing .card-footer {
        height: 100%;
        font-size: 0.8rem;
        padding: 0.4rem;
      }

      #footer {
        position: fixed;
        bottom: 0px;
        right: 0px;
        padding: 8px;
        font-size: 0.75rem;
        background-color: rgba(255,255,255,0.8);
        border-radius: 4px;
      }

      @media screen and (min-width: 1200px) {
        #plot-listing .card {
          max-width: 350px;
        }
      }

      @media screen and (min-width: 800px) and (max-width: 1199px) {
        #plot-listing .card {
          max-width: 300px;
        }
      }

      @media screen and (min-width: 668px) and (max-width: 799px) {
        #plot-listing .card {
          max-width: 250px;
        }
      }

      /* portrait mode, without pixel ratio setting */
      @media only screen and (max-height: 667px) and (orientation: portrait) {
        #plot-listing .card {
          max-width: 162px;
        }
      }

      /* landscape mode, without pixel ratio setting */
      @media only screen and (max-height: 667px) and (orientation: landscape) {
        #plot-listing .card {
          max-width: 202px;
        }
      }
    </style>

    <title>PlotBrowser</title>
  </head>

  <body>
    <!-- navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarSupportedContent">

          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                  <?php
                    // home
                    echo "<li class=\"breadcrumb-item\"><a href=\"/\"><i class=\"bi bi-house-door-fill\"></i></a></li>";

                    // path fragments
                    $rel_dir = trim(preg_replace("/(.*)\?.*/i", "$1", $_SERVER["REQUEST_URI"]), "/");
                    if ($rel_dir != "") {
                      $fragments = explode("/", $rel_dir);
                      foreach($fragments as $i=>$fragment) {
                        $href = implode("/", array_fill(0, count($fragments) - 1 - $i, ".."));
                        echo "<li class=\"breadcrumb-item\"><a href=\"$href\">$fragment</a></li>";
                      }
                    }
                  ?>
                </ol>
              </nav>
            </li>
          </ul>

          <form class="d-flex">
            <div class="input-group">
              <input class="form-control" type="search" name="search" placeholder="Pattern(s)" aria-label="Search" value="<?php if (isset($_GET["search"])) echo htmlspecialchars($_GET["search"]); ?>">
              <button class="btn btn-outline-success" type="submit">Search</button>
            </div>
          </form>

        </div>

      </div>
    </nav>

    <!-- show search info -->
    <?php
      if (isset($_GET["search"]) && !empty($_GET["search"])) {
        echo "<div id=\"search-description\" class=\"container-fluid\">";
        echo "<i>Searching for '<b>" . $_GET["search"] . "</b>'";
        if ($search_pattern_mode != "") {
          echo " (mode '" . $search_pattern_mode . "')";
        }
        echo " in all $n_searched_dirs folders";
        echo "</i></div>";
      }
    ?>

    <!-- list other directories -->
    <div id="directory-listing" class="container-fluid">
      <h4><a id="directories">Directories</a></h4>
      <?php
        $dir_names = array();
        foreach ($entries as $dir_name) {
          if (!is_dir($dir_name) || !show_entry($dir_name)) {
            continue;
          }
          array_push($dir_names, $dir_name);
        }
        if (count($dir_names) == 0) {
          echo "<span class=\"empty-text\">No directories to display</span>";
        } else {
          echo "<ul>";
          sort($dir_names);
          foreach($dir_names as $dir_name) {
            echo "<li><a href=\"$dir_name\">" . display_path($dir_name) . "</a></li>";
          }
          echo "</ul>";
        }
      ?>
    </div>

    <!-- list plots -->
    <div id="plot-listing" class="container-fluid">
      <h4><a id="plots">Plots</a></h4>
        <?php
          // plots grouped by the directory they are in
          $covered_files = array();
          $plot_groups = array();
          foreach ($entries as $plot_name) {
            if (!is_file($plot_name) || pathinfo($plot_name, PATHINFO_EXTENSION) != $main_extension || !show_entry($plot_name)) {
              continue;
            }
            $plot_groups[dirname($plot_name)][] = $plot_name;
          }
          if (count($plot_groups) == 0) {
            echo "<span class=\"empty-text\">No plots to display</span>";
          }
          ksort($plot_groups, SORT_STRING);
          foreach ($plot_groups as $dir_name => $plot_names) {
            // when searching, show each directory and its number of matching plots above them
            if ($search_recursive) {
              $n_plots = count($plot_names);
              $label = ($dir_name === $top_dir) ? "<i>top folder</i>" : display_path($dir_name);
              echo "<h5 class=\"plot-group\"><i class=\"bi bi-folder2-open\"></i> <a href=\"$dir_name\">$label</a>";
              echo " <span class=\"badge rounded-pill bg-secondary\">$n_plots " . ($n_plots == 1 ? "plot" : "plots") . "</span></h5>";
            }
            echo "<div class=\"d-flex align-content-start flex-wrap\">";
            sort($plot_names);
            foreach ($plot_names as $plot_name) {
              array_push($covered_files, $plot_name);
              echo "<div class=\"card text-center\">";

              echo "  <div class=\"card-header\">";
              echo "    <a href=\"$plot_name\">" . substr(basename($plot_name), 0, -4) . "</a>";
              echo "  </div>";
              echo "  <a href=\"$plot_name\">";
              echo "    <img class=\"card-img-top\" src=\"$plot_name\" loading=\"lazy\">";
              echo "  </a>";
              echo "  <div class=\"card-footer\">";
              echo "    <p class=\"card-text\">";

              $extension_links = array();
              foreach ($additional_extensions as $ext) {
                $other = str_replace(".$main_extension", ".$ext", $plot_name);
                if (file_exists($other) && show_entry($other)) {
                  array_push($covered_files, $other);
                  $badge_style = "secondary";
                  if ($ext == "png") {
                    $badge_style = "primary";
                  } else if ($ext == "pdf") {
                    $badge_style = "info";
                  } else if ($ext == "root") {
                    $badge_style = "dark";
                  } else if ($ext == "txt") {
                    $badge_style = "light";
                  }
                  array_push($extension_links, "<a href=\"$other\" class=\"badge rounded-pill bg-$badge_style\">$ext</a>");
                }
              }
              if (count($extension_links) == 0) {
                echo "<i>No other file extensions</i>";
              } else {
                echo implode(" ", $extension_links);
              }

              echo "    </p>";
              echo "  </div>";
              echo "</div>";
            }
            echo "</div>";
          }
        ?>
    </div>

    <!-- list additional files -->
    <div id="file-listing" class="container-fluid">
      <h4><a id="files">Other files</a></h4>
      <?php
        $file_names = array();
        foreach ($entries as $file_name) {
          // skip directories, index files, files already shown above, and manually skipped ones
          if (!is_file($file_name) || basename($file_name) == "index.php" || !show_entry($file_name) || in_array($file_name, $covered_files)) {
            continue;
          }
          array_push($file_names, $file_name);
        }

        if (count($file_names) == 0) {
          echo "<span class=\"empty-text\">No files to display</span>";
        } else {
          echo "<ul>";
          sort($file_names);
          foreach($file_names as $file_name) {
            echo "  <li><a href=\"$file_name\">" . display_path($file_name) . "</a></li>";
          }
          echo "</ul>";
        }
      ?>
    </div>

    <!-- scroll-to-top button -->
    <div class="container-fluid">
      <button type="button" class="btn btn-outline-primary btn-sm" id="scroll-top">To top</button>
    </div>

    <!-- footer -->
    <div id="footer">
      <a href="https://gitlab.cern.ch/cms-analysis/general/php-plots"><i class="bi bi-code-slash"></i> Plot browser</a>
      &nbsp;&nbsp;|&nbsp;&nbsp;
      <a href="https://cms-analysis.docs.cern.ch/guidelines/other/plot_browser"><i class="bi bi-info-circle"></i> Documentation</a>
    </div>

    <!-- include third-party scripts via cdns -->
    <script src="https://code.jquery.com/jquery-3.7.1.slim.min.js" integrity="sha256-kmHvs0B+OpCW5GVHUNjv9rOmY0IvSIRcf7zGUDTDQM8=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>

    <!-- inline scripts -->
    <script>
      $(document).ready(function() {
        // add event to scroll-to-top button
        $("#scroll-top").click(function() {
          window.scrollTo({top: 0, behavior: "smooth"});
        });
      });
    </script>
  </body>
</html>
