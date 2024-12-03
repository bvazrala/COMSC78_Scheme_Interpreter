(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

;; Problem 15
;; Returns a list of two-element lists
(define (enumerate s)
  (define (helper lst idx)
    (if (null? lst)
        '()
        (cons (list idx (car lst))
              (helper (cdr lst) (+ idx 1)))))
  (helper s 0))

;; Problem 16

;; Define mod function using remainder
(define (mod a b) (remainder a b))

;; Merge two lists S1 and S2 according to ORDERED? and return
;; the merged list.
(define (merge ordered? s1 s2)
  (cond ((null? s1) s2)
        ((null? s2) s1)
        ((ordered? (car s1) (car s2))
         (cons (car s1) (merge ordered? (cdr s1) s2)))
        (else
         (cons (car s2) (merge ordered? s1 (cdr s2))))))
