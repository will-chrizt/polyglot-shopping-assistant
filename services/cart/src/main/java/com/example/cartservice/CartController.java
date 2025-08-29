package com.example.cartservice;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/cart")
public class CartController {

    @Autowired
    private CartItemRepository cartItemRepository;

    @Autowired
    private CartService cartService; // Inject the new service

    @PostMapping("/add")
    public ResponseEntity<CartItem> addToCart(@RequestBody CartItem cartItem) {
        System.out.println("🛒 Received cart item:");
        System.out.println("Product ID: " + cartItem.getProductId());
        System.out.println("Name: " + cartItem.getName());
        System.out.println("Price: ₹" + cartItem.getPrice());

        CartItem savedItem = cartItemRepository.save(cartItem);
        return new ResponseEntity<>(savedItem, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<CartItem>> getCartItems() {
        List<CartItem> items = cartItemRepository.findAll();
        return new ResponseEntity<>(items, HttpStatus.OK);
    }

    // --- UPDATED METHOD ---
    @DeleteMapping("/remove/{id}")
    public ResponseEntity<Void> removeFromCart(@PathVariable Long id) {
        System.out.println("🗑️ Received request to remove item with ID: " + id);
        // Call the service method instead of the repository directly
        cartService.removeFromCart(id); 
        return ResponseEntity.ok().build();
    }
}