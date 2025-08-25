package com.example.order.controller;

import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
public class OrderController {

    static class Order {
        public String id;
        public String productId;
        public int qty;
        public String user;
    }

    private final Map<String, Order> ORDERS = new HashMap<>();

    @PostMapping("/orders")
    public Order create(@RequestBody Order req,
                        @RequestHeader(value = "Authorization", required = false) String auth) {
        // TODO: validate JWT from User Service using shared secret
        req.id = UUID.randomUUID().toString();
        ORDERS.put(req.id, req);
        return req;
    }

    @GetMapping("/orders/{id}")
    public Order get(@PathVariable String id,
                     @RequestHeader(value = "Authorization", required = false) String auth) {
        return ORDERS.get(id);
    }

    @GetMapping("/orders")
    public List<Order> list(@RequestHeader(value = "Authorization", required = false) String auth) {
        return new ArrayList<>(ORDERS.values());
    }
}
