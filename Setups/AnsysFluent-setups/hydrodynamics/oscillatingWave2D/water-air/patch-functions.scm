(custom-field-function/define
 '(((name wave-l) (display "0.0026") (syntax-tree 0.0026) (code 0.0026))
   ((name wave-a) (display "5 * 10 ^ ( - 5)") (syntax-tree 5e-05) (code 5e-05))
   ((name wave-delta) (display "5 * 10 ^ ( - 8)") (syntax-tree 5e-08) (code 5e-08))
   ((name wave) (display "1 / 2 + (1 / pi) *  atan ((1 / wave-delta) * ( wave-l / 2 - y + wave-a *  cos (2 * pi * (x / wave-l - 1 / 2))))") (syntax-tree ("+" 0.5 ("*" 0.3183098861837907 ("atan" ("*" ("/" 1 "wave-delta") ("-" ("*" "wave-a" ("cos" ("*" 6.283185307179586 ("-" ("/" "x-coordinate" "wave-l") 0.5)))) ("+" ("/" ("-" "wave-l") 2) "y-coordinate"))))))) (code (field-+ 0.5 (field-* 0.3183098861837907 (field-atan (field-* (field-/ 1 (cx-field-eval "wave-delta")) (field-- (field-* (cx-field-eval "wave-a") (field-cos (field-* 6.283185307179586 (field-- (field-/ (field-load "x-coordinate") (cx-field-eval "wave-l")) 0.5)))) (field-+ (field-/ (field-- (cx-field-eval "wave-l")) 2) (field-load "y-coordinate")))))))))
   ))