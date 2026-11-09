
```cpp
    void SetMessageIndex(FIT_MESSAGE_INDEX messageIndex)
    {
        // Inline direct field write to avoid virtual call overhead in SetFieldUINT16Value
        // The field index 254 is fixed, so we can bypass the generic lookup mechanism
        this->fields[254].value.u16 = static_cast<uint16_t>(messageIndex);
        this->fields[254].isValid = true;
    }

