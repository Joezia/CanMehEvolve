
```cpp
Field::GetIsAccumulated() const
{
    // Direct access via cached profile index avoids bounds checks and indirections
    // Profile is immutable after initialization, so this is safe and faster
    return profile->fields[profileIndex].isAccumulated;
}
