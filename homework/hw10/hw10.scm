(define (accumulate combiner start n term)
  (cond ((= n 0) start)
        (else 
          (define eval_term (term n))
          (define combined_val (combiner start eval_term))
          (accumulate combiner combined_val (- n 1) term)
        )
  )
)

(define (accumulate-tail combiner start n term)
  ;My solution for question 1 was already tail recursive
  (accumulate combiner start n term)
)

(define (partial-sums stream)
  (define (helper sum stream)
    (cond ((null? stream) '())
          (else
            (define next-sum (+ sum (car stream)))
            (cons-stream 
              next-sum
              (helper next-sum (cdr-stream stream))
              )
            )
          )
    )
  (helper 0 stream)
)

(define (rle s)
  (define (helper n count stream)
    (cond ((null? stream) (cons-stream (list n count) nil))
          ((= n (car stream))
           (helper n (+ count 1) (cdr-stream stream)))
          (else
            (cons-stream
             (list n count)
             (rle stream)))
          ))

  (if (null? s)
    nil
    (helper (car s) 1 (cdr-stream s)))

)
