
template <typename T>
T FieldBase::GetBitsValueT(const FIT_UINT16 offset, const FIT_UINT8 bits) const
{
    if (values.size() == 0)
        return FitInvalid<T>::value;

    T value = 0;
    FIT_UINT8 bitsRead = 0;
    FIT_UINT8 byteIdx = offset / 8;
    FIT_UINT8 bitOffset = offset % 8;

    while (bitsRead < bits)
    {
        if (byteIdx >= GetSize())
            return FitInvalid<T>::value;

        FIT_UINT8 data = GetValuesUINT8(byteIdx);
        FIT_UINT8 bitsInByte = 8 - bitOffset;
        FIT_UINT8 bitsToTake = std::min<FIT_UINT8>(bitsInByte, bits - bitsRead);

        FIT_UINT8 mask = (1 << bitsToTake) - 1;
        value |= static_cast<T>((data >> bitOffset) & mask) << bitsRead;

        bitsRead += bitsToTake;
        bitOffset = 0;
        byteIdx++;
    }

    return value;
}
