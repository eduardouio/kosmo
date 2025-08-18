<script setup>
</script>
<template>
  <div class="bg-gray-100 font-sansmx-auto">
    <div class="max-w-4xl mx-auto mt-10 p-6 bg-white shadow-lg border-2 border-orange-400 rounded-lg">
        <!-- Encabezado -->
        <div class="grid grid-cols-[70%_auto] items-center mb-6">
            <div>
                <img src="https://kosmoflowers.com/wp-content/uploads/2022/07/Mesa-de-trabajo-6.svg" class="h-15"/>
            </div>
            <div class="text-right">
                <div class="border-2 border-orange-400 p-2 rounded">
                    <div class="flex justify-end items-center mb-1">
                        <p class="text-sm font-bold text-right text-lg">Orden Compra:</p>
                        <p class="text-sm w-30 text-red-700 text-xl">000-000525</p>
                    </div>
                    <div class="flex justify-end items-center mb-1 border-t-2 border-green-500 pt-1">
                        <p class="text-sm font-bold text-right">Fecha:</p>
                        <p class="text-sm w-30 text-xl">12/03/2025</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="flex justify-between items-center mb-3 border-2 border-orange-400 p-2 rounded">
            <div>
                <div class="text-sm mt-2"><strong>Roses Grown by:</strong> KOSMO FLOWERS</div>
                <div class="text-sm"><strong>Address:</strong> Tupigachi - Tabacundo</div>
                <div class="text-sm"><strong>Country:</strong> ECUADOR</div>
            </div>
            <div class="text-right">
                <p class="text-sm mt-2"><strong>Email:</strong> invoices@kosmoflowers.com</p>
                <p class="text-sm"><strong>Phone:</strong> (+593) (9) 97753832</p>
            </div>
        </div>

        <!-- Información del cliente y adicional -->
        <div class="grid grid-cols-[60%_auto] gap-4 mb-6 text-sm">
            <!-- Información del cliente -->
            <div class="border-2 border-orange-400 p-4 rounded">
                <h2 class="text-lg font-semibold mb-2">CUSTOMER INFORMATION</h2>
                <p><strong class="text-gray-700">To:</strong> PREMIER FLORAL CORP</p>
                <p><strong class="text-gray-700">Address:</strong> 3555 NW 82nd AVE, Doral, FL 33122, United States</p>
                <p><strong class="text-gray-700">City - Count:</strong> Estados Unidos</p>
                <div class="flex justify-between">
                    <p><strong class="text-gray-700">E-mail:</strong> receiving@premierfloralcorp.com</p>
                    <p><strong class="text-gray-700">Credit:</strong> 45</p>
                </div>
            </div>
            <!-- Información adicional -->
            <div class="border-2 border-orange-400 p-4 rounded">
                <h2 class="text-lg font-semibold mb-2">Additional Information</h2>
                <p><strong>Date:</strong> 2024-03-21</p>
                <p><strong>Cargo Agency:</strong> LOGIZTIK ALLIANCE</p>
                <p><strong>M.A.W.B.:</strong> 145-0998 9143</p>
                <p><strong>H.A.W.B.:</strong> LA4034672429</p>
                <p><strong>DAE:</strong> 055-2024-40-00409229</p>
            </div>
        </div>

        <!-- Tabla de productos -->
        <div class="w-95 mb-6 min-w-full">
            <table class="text-sm">
                <thead>
                    <tr class="bg-orange-400">
                        <th class="border px-2 py-2 text-center text-wrap">BOXES</th>
                        <th class="border px-2 py-2 text-center text-wrap">SZ</th>
                        <th class="border px-2 py-2 text-center text-wrap">VARIETY</th>
                        <th class="border px-2 py-2 text-center text-wrap">STEM LENGTH</th>
                        <th class="border px-2 py-2 text-center text-wrap">BUNCHES</th>
                        <th class="border px-2 py-2 text-center text-wrap">STEMS / BUNCH</th>
                        <th class="border px-2 py-2 text-center text-wrap">TOTAL STEMS</th>
                        <th class="border px-2 py-2 text-center text-wrap">UNIT PRICE $</th>
                        <th class="border px-2 py-2 text-center text-wrap">TOTAL PRICE $</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="text-right">
                        <td class="border border-orange-400 px-4 py-2 w-1/12">2</td>
                        <td class="border border-orange-400 px-4 py-2">QB</td>
                        <td class="border border-orange-400 px-4 py-2 text-nowrap">NENA LOR DE LA COMUINA</td>
                        <td class="border border-orange-400 px-4 py-2">40</td>
                        <td class="border border-orange-400 px-4 py-2">25</td>
                        <td class="border border-orange-400 px-4 py-2">5</td>
                        <td class="border border-orange-400 px-4 py-2">250</td>
                        <td class="border border-orange-400 px-4 py-2">$0.32</td>
                        <td class="border border-orange-400 px-4 py-2">$80.00</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Total Factura -->
        <div class="text-right mb-6">
            <p class="text-lg font-bold">TOTAL FACTURA $150.00</p>
        </div>

        <!-- Resumen de totales -->
        <div class="grid grid-cols-2 gap-4 mb-6">
            <div>
                <p><strong>TOTAL HB:</strong> 0</p>
                <p><strong>TOTAL QB:</strong> 4</p>
                <p><strong>TOTAL PIECES:</strong> 4</p>
            </div>
            <div>
                <p><strong>TOTAL FB:</strong> 1</p>
                <p><strong>TOTAL TALLOS:</strong> 500</p>
            </div>
        </div>

        <!-- Nota -->
        <p class="text-sm italic">
            All prices are F.O.B. Quito, please remember that you have 10 days after the date on the invoice to make a claim and that we do not accept credits for freight or handling charges in any case.
        </p>
    </div>
</div>
</template>