package com.example.infoweb.converter;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

import java.io.IOException;

@Converter
public class EmbeddingConverter implements AttributeConverter<double[], String> {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public String convertToDatabaseColumn(double[] attribute) {
        try {
            return objectMapper.writeValueAsString(attribute);
        } catch (JsonProcessingException e) {
            // 예외 처리
            return null;
        }
    }

    @Override
    public double[] convertToEntityAttribute(String dbData) {
        try {
            return objectMapper.readValue(dbData, double[].class);
        } catch (IOException e) {
            // 예외 처리
            return null;
        }
    }
}
