(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

; Some utility functions that you may find useful to implement.

(define (cons-all first rests)
  (if (null? rests)
    nil
    (cons (cons first (car rests)) (cons-all first (cdr rests)))  )
  )

(define (zip pairs)
  (cond ((null? pairs) '('() '()))
        ((null? (car pairs)) nil)
        (else
            (append
              (list (map car pairs))
              (zip (map cdr pairs))
            )
        )
  )
  )

;;Errors in my compiler, these should work in normal scheme

;; Problem 17
;; Returns a list of two-element lists
(define (enumerate s)
  ; BEGIN PROBLEM 17
  (define nums '())
  (define (num-helper n)
    (cond ((< n (length s))
            (append nums '(n))
            (num-helper (+ n 1))
            )
          )
    )
  (num-helper 0)
  (zip '(nums s))
  )
  ; END PROBLEM 17

(define (reverse s)
  (define (helperfn s reversed)
      (cond ((null? s) reversed)
          (else (helperfn (cdr s) (cons (car s)
                      reversed)))))
  (helperfn s nil))

;; Problem 18
;; List all ways to make change for TOTAL with DENOMS
(define (list-change total denoms)
  ; BEGIN PROBLEM 18

(define (helperfn total_val denoms sum-list)
      (cond
          ((null? denoms) nil)
          ((zero? total_val) (list sum-list))
          ((> (car denoms) total_val) (helperfn total_val (cdr denoms) sum-list))
          (else (append
                    (helperfn (- total_val (car denoms))
                            denoms (cons (car denoms) sum-list))
                    (helperfn total_val (cdr denoms) sum-list)))))
  (map reverse (helper total denoms nil))

  )
  ; END PROBLEM 18

;; Problem 19
;; Returns a function that checks if an expression is the special form FORM
(define (check-special form)
  (lambda (expr) (equal? form (car expr))))

(define lambda? (check-special 'lambda))
(define define? (check-special 'define))
(define quoted? (check-special 'quote))
(define let?    (check-special 'let))

(define (eval-list eval-fn expr)
  (if (null? expr) nil
       (cons (eval-fn (car expr)) (eval-list eval-fn (cdr expr)))))


;; Converts all let special forms in EXPR into equivalent forms using lambda
(define (let-to-lambda expr)
  (cond ((atom? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((quoted? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((or (lambda? expr)
             (define? expr))
         (let ((form   (car expr))
               (params (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19
           (define eval_body (eval-list let-to-lambda body))
           (append (list form params) eval_body)

           ; END PROBLEM 19
           ))
        ((let? expr)
         (let ((values (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19
           (define eval_body (eval-list let-to-lambda
                                            body))
           (define eval-params (eval-list let-to-lambda
              (cadr (zip values))))
              (cons (append (list 'lambda (car (zip values))) eval_body)
                 eval-params)

           ; END PROBLEM 19
           ))
        (else
         ; BEGIN PROBLEM 19
         (eval-list let-to-lambda expr)
         ; END PROBLEM 19
         )))
