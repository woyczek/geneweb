(* camlp4r ./pa_html.cmo *)
(* $Id: wiki.ml,v 4.6 2005-07-07 19:33:53 ddr Exp $ *)
(* Copyright (c) 1998-2005 INRIA *)

open Config;
open Printf;
open Util;

(* TLSW: Text Language Stolen to Wikipedia
   = title level 1 =
   == title level 2 ==
   ...
   ====== title level 6 ======
   * list ul/li item
   * list ul/li item
   ** list ul/li item 2nd level
   ** list ul/li item 2nd level
   ...
   [[first_name/surname/oc/text]] link; 'text' displayed
   [[first_name/surname/text]] link (oc = 0); 'text' displayed
   [[first_name/surname]] link (oc = 0); 'first_name surname' displayed
   [[[notes_subfile/text]]] link to a sub-file; 'text' displayed
   [[[notes_subfile]]] link to a sub-file; 'notes_subfile' displayed
   __TOC__ : summary
   __SHORT_TOC__ : short summary (unnumbered)
   __NOTOC__ : no (automatic) numbered summary *)

module Buff = Buff.Make (struct value buff = ref (String.create 80); end);

value first_cnt = 1;

value tab lev s = String.make (2 * lev) ' ' ^ s;

value section_level s len =
  loop 1 (len - 2) 4 where rec loop i j k =
    if i > 5 then i
    else if len > k && s.[i] = '=' && s.[j] = '=' then
      loop (i + 1) (j - 1) (k + 2)
    else i
;

value adjust_ul_level rev_lines old_lev new_lev =
  if old_lev < new_lev then [tab (old_lev + 1) "<ul>" :: rev_lines]
  else
    let rev_lines = [List.hd rev_lines ^ "</li>" :: List.tl rev_lines] in
    loop rev_lines old_lev where rec loop rev_lines lev =
      if lev = new_lev then rev_lines
      else loop [tab lev "</ul></li>" :: rev_lines] (lev - 1)
;

value message_txt conf i = transl_nth conf "visualize/show/hide/summary" i;

value summary_of_tlsw_lines conf short lines =
  let (rev_summary, lev, _, cnt, rev_sections_nums) =
    List.fold_left
      (fun (summary, prev_lev, indent_stack, cnt, sections_nums) s ->
        let len = String.length s in
        if len > 2 && s.[0] = '=' && s.[len-1] = '=' then
          let slev = section_level s len in
          let (lev, stack) =
            loop prev_lev indent_stack where rec loop lev stack =
              match stack with
              [ [(prev_num, prev_slev) :: rest_stack] ->
                  if slev < prev_slev then
                    match rest_stack with
                    [ [(_, prev_prev_slev) :: _] ->
                        if slev > prev_prev_slev then
                          let stack = [(prev_num, slev) :: rest_stack] in
                          loop lev stack
                        else
                          loop (lev - 1) rest_stack
                    | [] ->
                        let stack = [(prev_num + 1, slev) :: rest_stack] in
                        (lev - 1, stack) ]
                  else if slev = prev_slev then
                    let stack = [(prev_num + 1, slev) :: rest_stack] in
                    (lev - 1, stack)
                  else
                    let stack = [(1, slev) :: stack] in
                    (lev, stack)
              | [] ->
                  let stack = [(1, slev) :: stack] in
                  (lev, stack) ]
          in
          let section_num =
            let nums = List.map fst stack in
            String.concat "." (List.rev_map string_of_int nums)
          in
          let summary =
            let s =
              sprintf "<a href=\"#a_%d\">%s%s</a>" cnt
                (if short then "" else section_num ^ " - ")
                (Gutil.strip_spaces (String.sub s slev (len - 2 * slev)))
            in
            if short then
              if summary = [] then [s] else [s; ";" :: summary]
            else
              let line = tab (lev + 1) "<li>" ^ s in
              [line :: adjust_ul_level summary (prev_lev - 1) lev]
          in
          (summary, lev + 1, stack, cnt + 1, [section_num :: sections_nums])
        else (summary, prev_lev, indent_stack, cnt, sections_nums))
      ([], 0, [], first_cnt, []) lines
  in
  if cnt <= first_cnt + 1 then
    (* less that 2 paragraphs : summary abandonned *)
    ([], [])
  else
    let rev_summary =
      if short then rev_summary
      else ["</ul>" :: adjust_ul_level rev_summary (lev - 1) 0]
    in
    let lines =
      ["<dl><dd>";
       "<table border=\"1\" cellpadding=\"10\">";
       "<tr><td align=\"" ^ conf.left ^ "\">";
       "<div style=\"text-align:center\"><b>" ^
          capitale (message_txt conf 3) ^ "</b>";
       "<script type=\"text/javascript\">";
       "//<![CDATA[";
       "showTocToggle()";
       "//]]>";
       "</script>";
       "</div>";
       "<div class=\"summary\" id=\"tocinside\">" ::
       List.rev_append rev_summary
         ["</div>";
          "</td></tr></table>";
          "</dd></dl>"]]
    in
    (lines, List.rev rev_sections_nums)
;

value rec syntax_lists conf wlo list =
  fun
  [ ["__NOTOC__" :: sl] -> syntax_lists conf wlo list sl
  | ["__TOC__" :: sl] ->
      let list =
        match wlo with
        [ Some lines ->
            let (summary, _) = summary_of_tlsw_lines conf False lines in
            List.rev_append summary list
        | None -> list ]
      in
      syntax_lists conf wlo list sl
  | ["__SHORT_TOC__" :: sl] ->
      let list =
        match wlo with
        [ Some lines ->
            let (summary, _) = summary_of_tlsw_lines conf True lines in
            List.rev_append summary list
        | None -> list ]
      in
      syntax_lists conf wlo list sl
  | [s :: sl] ->
      if String.length s > 0 && s.[0] = '*' then
        let (sl, rest) = select_list_lines conf [] [s :: sl] in
        let list = syntax_ul 0 list sl in
        syntax_lists conf wlo list rest
      else syntax_lists conf wlo [s :: list] sl
  | [] -> List.rev list ]
and select_list_lines conf list =
  fun
  [ [s :: sl] ->
      let len = String.length s in
      if len > 0 && s.[0] = '*' then
        let s = String.sub s 1 (len - 1) in
        let (s, sl) =
          loop s sl where rec loop s1 =
            fun
            [ [""; s :: sl]
              when String.length s > 1 && s.[0] = '*' && s.[1] = '*' ->
                let br = "<br" ^ conf.xhs ^ ">" in
                loop (s1 ^ br ^ br) [s :: sl]
            | [s :: sl] ->
                if String.length s > 0 && s.[0] <> '*' then
                  loop (s1 ^ "\n" ^ s) sl
                else (s1, [s :: sl])
            | [] -> (s1, []) ]
        in
        select_list_lines conf [s :: list] sl
      else (List.rev list, [s :: sl])
  | [] -> (List.rev list, []) ]
and syntax_ul lev list sl =
  let list = [tab lev "<ul>" :: list] in
  let list =
    loop list sl where rec loop list =
      fun
      [ [s1; s2 :: sl] ->
          if String.length s2 > 0 && s2.[0] = '*' then
            let list = [tab lev "<li>" ^ s1 :: list] in
            let (list2, sl) =
              loop [] [s2 :: sl] where rec loop list =
                fun
                [ [s :: sl] ->
                    if String.length s > 0 && s.[0] = '*' then
                      let s = String.sub s 1 (String.length s - 1) in
                      loop [s :: list] sl
                    else (list, [s :: sl])
                | [] -> (list, []) ]
            in
            let list = syntax_ul (lev + 1) list (List.rev list2) in
            loop [tab lev "</li>" :: list] sl
          else
            loop [tab lev "<li>" ^ s1 ^ "</li>" :: list] [s2 :: sl]
      | [s] -> [tab lev "<li>" ^ s ^ "</li>" :: list]
      | [] -> list ]
  in
  [tab lev "</ul>" :: list]
;

value rev_syntax_lists conf wlo list rev_list =
  syntax_lists conf wlo list (List.rev rev_list)
;

value syntax_links conf mode file_path s =
  let slen = String.length s in
  loop 0 0 where rec loop i len =
    if i = slen then Buff.get len
    else if
      s.[i] = '%' && i < slen - 1 && List.mem s.[i+1] ['['; ']'; '{'; '}']
    then
      loop (i + 2) (Buff.store len s.[i+1])
    else if s.[i] = '{' then
      let j =
        loop (i + 1) where rec loop j =
          if j = slen then j
          else if s.[j] = '}' then j + 1
          else loop (j + 1)
      in
      let b = String.sub s (i + 1) (j - i - 2) in
      loop j (Buff.mstore len (sprintf "<span class=\"highlight\">%s</span>" b))
    else if i < slen - 2 && s.[i] = '[' && s.[i+1] = '[' && s.[i+2] = '[' then
      match Gutil.ext_file_link s i with
      [ Some (j, fname, sname, text) ->
          let c =
            let f = file_path fname in
            if Sys.file_exists f then "" else " style=\"color:red\""
          in
          let t =
            sprintf "<a href=\"%sm=%s;f=%s%s\"%s>%s</a>"
              (commd conf) mode fname sname c text
          in
          loop j (Buff.mstore len t)
      | None -> loop (i + 3) (Buff.mstore len "[[[") ]
    else if i < slen - 1 && s.[i] = '[' && s.[i+1] = '[' then
      let j =
        loop (i + 2) where rec loop j =
          if j = slen then j
          else if j < slen - 1 && s.[j] = ']' && s.[j+1] = ']' then j + 2
          else loop (j + 1)
      in
      let t =
        let b = String.sub s (i + 2) (j - i - 4) in
        try
          let k = 0 in
          let l = String.index_from b k '/' in
          let fn = String.sub b k (l - k) in
          let k = l + 1 in
          let (fn, sn, oc, name) =
            try
              let l = String.index_from b k '/' in
              let sn = String.sub b k (l - k) in
              let (oc, name) =
                try
                  let k = l + 1 in
                  let l = String.index_from b k '/' in
                  let x = String.sub b k (l - k) in
                  (x, String.sub b (l + 1) (String.length b - l - 1))
                with
                [ Not_found ->
                    ("", String.sub b (l + 1) (String.length b - l - 1)) ]
              in
              (fn, sn, oc, name)
            with
            [ Not_found ->
                let sn = String.sub b k (String.length b - k) in
                let name = fn ^ " " ^ sn in
                (fn, sn, "", name) ]
          in
          sprintf "<a href=\"%sp=%s;n=%s%s\">%s</a>" (commd conf)
            (code_varenv (Name.lower fn)) (code_varenv (Name.lower sn))
            (if oc = "" then "" else ";oc=" ^ oc) name
        with
        [ Not_found -> "[[" ^ b ^ "]]" ]
      in
      loop j (Buff.mstore len t)
    else loop (i + 1) (Buff.store len s.[i])
;

value no_auto_toc_list = ["__NOTOC__"; "__TOC__"; "__SHORT_TOC__"];

value lines_list_of_string s =
  loop False [] 0 0 where rec loop no_toc lines len i =
    if i = String.length s then
      (List.rev (if len = 0 then lines else [Buff.get len :: lines]), no_toc)
    else if s.[i] = '\n' then
      let line = Buff.get len in
      let no_toc = List.mem line no_auto_toc_list || no_toc in
      loop no_toc [line :: lines] 0 (i + 1)
    else
      loop no_toc lines (Buff.store len s.[i]) (i + 1)
;

value string_of_modify_link conf mode cnt sfn empty =
  sprintf "%s(<a href=\"%sm=MOD_%s;v=%d%s\">%s</a>)%s\n"
    (if empty then "<p>"
     else
       "<div style=\"float:" ^ conf.right ^ ";margin-" ^ conf.left ^
       ":3em\">")
    (commd conf) mode cnt sfn (transl_decline conf "modify" "")
    (if empty then "</p>" else "</div>")
;

value gen_html_of_tlsw_lines wlo conf mode_opt sub_fname cnt0 lines
    sections_nums =
  let sfn = if sub_fname = "" then "" else ";f=" ^ sub_fname in
  let (rev_lines, _, _) =
    List.fold_left
      (fun (lines, cnt, sections_nums) s ->
         let len = String.length s in
         if len > 2 && s.[0] = '=' && s.[len-1] = '=' then
           let lev = section_level s len in
           let (section_num, sections_nums) =
             match sections_nums with
             [ [a :: l] -> (a ^ " - ", l)
             | [] -> ("", []) ]
           in
           let s =
             sprintf "<h%d>%s%s%s</h%d>" lev section_num
               (String.sub s lev (len-2*lev))
               (if lev <= 3 then "<hr" ^ conf.xhs ^ ">" else "") lev
           in
           match mode_opt with
           [ Some mode ->
               let n1 =
                 if conf.wizard then
                   string_of_modify_link conf mode cnt sfn False
                 else ""
               in
               let n2 =
                 sprintf "<p><a name=\"a_%d\" id=\"a_%d\"></a></p>" cnt cnt
               in
               ([s; n1; n2 :: lines], cnt + 1, sections_nums)
           | None -> ([s :: lines], cnt + 1, sections_nums) ]
         else ([s :: lines], cnt, sections_nums))
      ([], max cnt0 first_cnt, sections_nums) lines
  in
  rev_syntax_lists conf wlo [] rev_lines
;

value html_of_tlsw_lines = gen_html_of_tlsw_lines None;

value html_of_tlsw conf s =
  let (lines, _) = lines_list_of_string s in
  html_of_tlsw_lines conf None "" 0 lines []
;

value html_with_summary_of_tlsw conf mode file_path sub_fname s =
  let (lines, no_toc) = lines_list_of_string s in
  let (summary, sections_nums) =
    if no_toc then ([], []) else summary_of_tlsw_lines conf False lines
  in
  let (rev_lines_before_summary, lines) =
    loop [] lines where rec loop lines_bef =
      fun
      [ [s :: sl] ->
          if String.length s > 1 && s.[0] = '=' then (lines_bef, [s :: sl])
          else loop [s :: lines_bef] sl
      | [] -> (lines_bef, []) ]
  in
  let lines_before_summary =
    rev_syntax_lists conf (Some lines) [] rev_lines_before_summary
  in
  let lines_after_summary =
    gen_html_of_tlsw_lines (Some lines) conf (Some mode) sub_fname first_cnt
      lines sections_nums
  in
  let s =
    syntax_links conf mode file_path
      (String.concat "\n"
        (lines_before_summary @ summary @ lines_after_summary))
  in
  if conf.wizard && (lines_before_summary <> [] || lines = []) then
    let sfn = if sub_fname = "" then "" else ";f=" ^ sub_fname in
    string_of_modify_link conf mode 0 sfn (s = "") ^ s
  else s
;

value rev_extract_sub_part s v =
  let (lines, _) = lines_list_of_string s in
  loop [] 0 first_cnt lines where rec loop lines lev cnt =
    fun
    [ [s :: sl] ->
        let len = String.length s in
        if len > 2 && s.[0] = '=' && s.[len-1] = '=' then
          if v = first_cnt - 1 then lines
          else
            let nlev = section_level s len in
            if cnt = v then loop [s :: lines] nlev (cnt + 1) sl
            else if cnt > v then
              if nlev > lev then loop [s :: lines] lev (cnt + 1) sl
              else lines
            else loop lines lev (cnt + 1) sl
        else if cnt <= v then loop lines lev cnt sl
        else loop [s :: lines] lev cnt sl
    | [] -> lines ]
;

value extract_sub_part s v = List.rev (rev_extract_sub_part s v);

value print_sub_part conf file_path mode sub_fname cnt0 lines ending_filter =
  let lines =
    List.map
      (fun
       [ "__TOC__" | "__SHORT_TOC__" ->
           sprintf "<p>...%s...</p>" (message_txt conf 3)
       | "__NOTOC__" -> ""
       | s -> s ])
      lines
  in
  let lines = html_of_tlsw_lines conf (Some mode) sub_fname cnt0 lines [] in
  let s = String.concat "\n" lines in
  let s = syntax_links conf mode file_path s in
  let s = ending_filter s in
  let sfn = if sub_fname = "" then "" else ";f=" ^ sub_fname in
  let s =
    if cnt0 < first_cnt && conf.wizard then
      string_of_modify_link conf mode 0 sfn (s = "") ^ s
    else s
  in
  do {
    tag "p" begin
      if cnt0 >= first_cnt then do {
        stag "a" "href=\"%sm=%s;v=%d%s\"" (commd conf) mode (cnt0 - 1) sfn begin
          Wserver.wprint "&lt;&lt;";
        end;
        Wserver.wprint "\n";
      }
      else ();
      if cnt0 >= first_cnt - 1 then do {
        stag "a" "href=\"%sm=%s%s\"" (commd conf) mode sfn begin
          Wserver.wprint "^^";
        end;
        Wserver.wprint "\n";
      }
      else ();
      if s <> "" then do {
        stag "a" "href=\"%sm=%s;v=%d%s\"" (commd conf) mode (cnt0 + 1) sfn begin
          Wserver.wprint "&gt;&gt;";
        end;
        Wserver.wprint "\n";
      }
      else ();
    end;
    Wserver.wprint "%s\n" s
  }
;

value print_mod_page conf mode fname title ntitle s =
  let s = if ntitle = "" then s else ntitle ^ "\n" ^ s in
  let (has_v, v) =
    match p_getint conf.env "v" with
    [ Some v -> (True, v)
    | None -> (False, 0) ]
  in
  let sub_part =
    if not has_v then s else String.concat "\n" (extract_sub_part s v)
  in
  let sfn = if fname = "" then "" else ";f=" ^ fname in
  do {
    header conf title;
    tag "div" "style=\"float:%s;margin-%s:5px\"" conf.right conf.left begin
      stag "a" "href=\"%sm=%s%s%s\"" (commd conf) mode
        (if has_v then ";v=" ^ string_of_int v else "") sfn
      begin
        Wserver.wprint "(%s)\n" (message_txt conf 0);
      end;
    end;
    print_link_to_welcome conf False;
    if has_v then
      tag "p" begin
        if v >= first_cnt then do {
          stag "a" "href=\"%sm=MOD_%s;v=%d%s\"" (commd conf) mode (v - 1) sfn
          begin
            Wserver.wprint "&lt;&lt;";
          end;
          Wserver.wprint "\n";
        }
        else ();
        if sub_part <> "" then do {
          stag "a" "href=\"%sm=MOD_%s;v=%d%s\"" (commd conf) mode (v + 1) sfn
          begin
            Wserver.wprint "&gt;&gt;";
          end;
          Wserver.wprint "\n";
        }
        else ();
      end
    else ();
    tag "form" "method=\"post\" action=\"%s\"" conf.command begin
      tag "p" begin
        Util.hidden_env conf;
        xtag "input" "type=\"hidden\" name=\"m\" value=\"MOD_%s_OK\"" mode;
        if has_v then
          xtag "input" "type=\"hidden\" name=\"v\" value=\"%d\"" v
        else ();
        if fname <> "" then
          xtag "input" "type=\"hidden\" name=\"f\" value=\"%s\"" fname
        else ();
        let digest = Iovalue.digest s in
        xtag "input" "type=\"hidden\" name=\"digest\" value=\"%s\"" digest;
        stagn "textarea" "name=\"notes\" rows=\"30\" cols=\"110\"" begin
          if sub_part <> "" then Wserver.wprint "%s" (quote_escaped sub_part)
          else ();
        end;
      end;
      tag "p" begin
        xtag "input" "type=\"submit\" value=\"Ok\"";
      end;
    end;
    trailer conf;
  }
;

value insert_sub_part s v sub_part =
  let (lines, _) = lines_list_of_string s in
  let (lines, sl) =
    loop False [] 0 first_cnt lines
    where rec loop sub_part_added lines lev cnt =
      fun
      [ [s :: sl] ->
          let len = String.length s in
          if len > 2 && s.[0] = '=' && s.[len-1] = '=' then
            if v = first_cnt - 1 then
              (if sub_part = "" then [] else [""; sub_part], [s :: sl])
            else
              let nlev = section_level s len in
              if cnt = v then
                let lines =
                  if sub_part = "" then lines else [""; sub_part :: lines]
                in
                loop True lines nlev (cnt + 1) sl
              else if cnt > v then
                if nlev > lev then loop sub_part_added lines lev (cnt + 1) sl
                else (lines, [s :: sl])
              else loop sub_part_added [s :: lines] lev (cnt + 1) sl
            else if cnt <= v then loop sub_part_added [s :: lines] lev cnt sl
            else loop sub_part_added lines lev cnt sl
      | [] ->
          let lines =
            if sub_part_added then lines
            else if sub_part = "" then lines
            else [""; sub_part :: lines]
          in
          (lines, []) ]
  in
  String.concat "\n" (List.rev_append lines sl)
;

value split_title_and_text s =
  let (tit, txt) =
    try
      let i = String.index s '\n' in
      let tit = String.sub s 0 i in
      let txt = String.sub s (i + 1) (String.length s - i - 1) in
      (tit, txt)
    with
    [ Not_found -> (s, "") ]
  in
  if String.length tit > 0 && tit.[0] = '=' || String.contains tit '<'
  || String.contains tit '['
  then
    ("", s)
  else (tit, txt)

;
