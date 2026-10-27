syncplots() {
    local src=/t3home/zoghafoo/WMassNanoProduction/new_plots
    local dst=/eos/user/z/zoghafoo/www
    local stamp=/t3home/zoghafoo/.new_plots_last_sync
    local failed=0 f d rel
    export EOS_MGM_URL=root://eosuser.cern.ch

    # without this, a missing src would delete everything on EOS below
    [ -d "$src" ] || { echo "$src not found"; return 1; }

    # give new folders an index.php (-n leaves existing ones untouched)
    find "$src" -mindepth 1 -type d -exec cp -n /t3home/zoghafoo/index.php {} \;

    # only look at things changed since the last successful sync
    local newer=()
    [ -e "$stamp" ] && newer=(-newer "$stamp")
    touch "$stamp.new"

    while IFS= read -r -d '' d; do
        eos mkdir -p "$dst/${d#$src/}" || failed=1
    done < <(find "$src" -mindepth 1 -type d "${newer[@]}" -print0)

    while IFS= read -r -d '' f; do
        rel=${f#$src/}
        echo "-> $rel"
        eos cp -s "$f" "$dst/$rel" || failed=1
    done < <(find "$src" -type f "${newer[@]}" -print0)

    # delete whatever no longer exists here; a whole missing folder goes with one rm -r
    while IFS= read -r d; do
        d=${d%/}
        [ "$d" = "$dst" ] && continue
        rel=${d#$dst/}
        [ -d "$src/$rel" ] && continue
        [ -d "$src/$(dirname "$rel")" ] || continue   # parent is removed instead
        echo "rm $rel/"
        eos rm -r "$d" || failed=1
    done < <(eos find -d "$dst" | grep -v '/\.sys\.')

    while IFS= read -r f; do
        rel=${f#$dst/}
        [ -e "$src/$rel" ] && continue
        [ -d "$src/$(dirname "$rel")" ] || continue   # already gone with its folder
        echo "rm $rel"
        eos rm "$f" || failed=1
    done < <(eos find -f "$dst" | grep -v '/\.sys\.')

    if [ $failed -eq 0 ]; then
        mv "$stamp.new" "$stamp"
    else
        rm -f "$stamp.new"
        echo "Some copies failed; they will be retried next time."
    fi
}
