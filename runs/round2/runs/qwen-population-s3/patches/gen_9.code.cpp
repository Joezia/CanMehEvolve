
void FieldBase::AddRawValue(const FIT_FLOAT64 rawValue, const FIT_UINT8 fieldArrayIndex)
{
    FIT_FLOAT64 roundedValue = FieldBase::Round(rawValue);
    switch (GetType())
    {
        case FIT_BASE_TYPE_BYTE:
        case FIT_BASE_TYPE_ENUM:
        case FIT_BASE_TYPE_SINT8:
        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
            SetUINT8Value((FIT_UINT8)roundedValue, fieldArrayIndex);
            break;

        case FIT_BASE_TYPE_SINT16:
        case FIT_BASE_TYPE_UINT16:
        case FIT_BASE_TYPE_UINT16Z:
            SetUINT16Value((FIT_UINT16)roundedValue, fieldArrayIndex);
            break;

        case FIT_BASE_TYPE_SINT32:
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
            SetUINT32Value((FIT_UINT32)roundedValue, fieldArrayIndex);
            break;

        case FIT_BASE_TYPE_FLOAT32:
        {
            FIT_FLOAT32 float32Value = static_cast<FIT_FLOAT32>(roundedValue);
            FIT_UINT32 uint32Value;
            std::memcpy(&uint32Value, &float32Value, sizeof(FIT_FLOAT32));
            SetUINT32Value(uint32Value, fieldArrayIndex);
            break;
        }

        case FIT_BASE_TYPE_FLOAT64:
        {
            const size_t neededSize = (fieldArrayIndex + 1) * 8;
            if (values.size() < neededSize)
            {
                values.resize(neededSize);
            }
            std::memcpy(&values[fieldArrayIndex * 8], &rawValue, 8);
            break;
        }

        case FIT_BASE_TYPE_SINT64:
            SetSINT64Value(*reinterpret_cast<const FIT_SINT64*>(&rawValue), fieldArrayIndex);
            break;

        case FIT_BASE_TYPE_UINT64:
        case FIT_BASE_TYPE_UINT64Z:
            SetUINT64Value(*reinterpret_cast<const FIT_UINT64*>(&rawValue), fieldArrayIndex);
            break;

        default:
            break;
    }
}
