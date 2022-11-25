(custom-field-function/define
 '(((name x0) (display "0.5") (syntax-tree 0.5) (code 0.5))
   ((name y0) (display "0.5") (syntax-tree 0.5) (code 0.5))
   ((name r0) (display "0.25") (syntax-tree 0.25) (code 0.25))
   ((name delta) (display "0.001") (syntax-tree 0.001) (code 0.001))
   ((name droplet) (display "1 / 2 +  atan ((r0 - sqrt ((x - x0) ^ 2 + (y - y0) ^ 2)) / (r0 * delta)) / pi") (syntax-tree ("+" 0.5 ("/" ("atan" ("/" ("-" "r0" ("sqrt" ("+" ("**" ("-" "x-coordinate" "x0") 2) ("**" ("-" "y-coordinate" "y0") 2)))) ("*" "r0" "delta"))) 3.141592653589793))) (code (field-+ 0.5 (field-/ (field-atan (field-/ (field-- (cx-field-eval "r0") (field-sqrt (field-+ (field-** (field-- (field-load "x-coordinate") (cx-field-eval "x0")) 2) (field-** (field-- (field-load "y-coordinate") (cx-field-eval "y0")) 2)))) (field-* (cx-field-eval "r0") (cx-field-eval "delta")))) 3.141592653589793))))
   ))