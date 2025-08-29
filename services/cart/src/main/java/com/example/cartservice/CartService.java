package com.example.cartservice;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional; // Import this

@Service
public class CartService {

    @Autowired
    private CartItemRepository cartItemRepository;

    @Transactional // This is the crucial annotation
    public void removeFromCart(Long id) {
        cartItemRepository.deleteById(id);
    }
}