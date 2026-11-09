
```cpp
    void SetText(FIT_WSTRING text)
    {
        const FIT_WSTRING& ref = text;
        SetFieldSTRINGValue(1, ref, 0);
    }
